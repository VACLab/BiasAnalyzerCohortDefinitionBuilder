# builder.py
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
import os
import tempfile
import weakref
import atexit
import yaml

from CohortDefinition.events import Event

# ---------- Internal token to prevent direct TemporalBlock construction ----------
class _Token:
    pass
TOKEN = _Token()

# Track all temp YAML files for best-effort cleanup at interpreter exit
_TEMP_YAML_PATHS = set()

def _cleanup_all_temp_yaml():
    """Best-effort remove all temp YAML files created by CohortCriteria."""
    for p in list(_TEMP_YAML_PATHS):
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
        finally:
            _TEMP_YAML_PATHS.discard(p)

atexit.register(_cleanup_all_temp_yaml)


# ---------- Single-quoted string support ----------
class SingleQuoted(str):
    """Mark a string value to be emitted with single quotes."""
    pass

def _single_quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

yaml.add_representer(SingleQuoted, _single_quoted_str_representer)

# ---------- Flow-style list support (e.g., [a, b]) ----------
class FlowList(list):
    """Force flow style for specific lists (e.g., interval)."""
    pass

def _flow_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(FlowList, _flow_list_representer)

# ---------- Demographics ----------
@dataclass
class Demographics:
    gender: Optional[str] = None
    min_birth_year: Optional[int] = None
    max_birth_year: Optional[int] = None

    def to_yaml(self) -> Dict[str, Any]:
        """Return demographics as a plain YAML-ready dict."""
        d: Dict[str, Any] = {}
        if self.gender:
            d["gender"] = SingleQuoted(self.gender)
        if self.min_birth_year is not None:
            d["min_birth_year"] = int(self.min_birth_year)
        if self.max_birth_year is not None:
            d["max_birth_year"] = int(self.max_birth_year)
        return d

# ---------- Helpers ----------
def _as_yaml(x: Union[Event, Dict[str, Any], "TemporalBlock"]) -> Dict[str, Any]:
    """
    Convert a supported operand (Event | TemporalBlock | dict) to a plain YAML dict.
    - Event -> .to_yaml_event()
    - TemporalBlock -> .to_yaml()
    - dict -> as is
    """
    # Import here to avoid circular imports
    from .builder import TemporalBlock as _TB  # type: ignore
    if isinstance(x, Event):
        return x.to_yaml_event()
    if isinstance(x, dict):
        return x
    if isinstance(x, _TB):
        return x.to_yaml()
    raise TypeError(f"Unsupported temporal block element: {type(x)}")

def _assert_operator_arity_or_raise(op: str, events_len: int) -> None:
    """Guardrail: ensure operator has exactly the required number of events."""
    if op in {"AND", "OR", "BEFORE", "AFTER"}:
        expected = 2
    elif op == "NOT":
        expected = 1
    else:
        return
    if events_len != expected:
        raise ValueError(f"Operator {op!r} requires exactly {expected} event(s), got {events_len}.")

# ---------- TemporalBlock ----------
@dataclass
class TemporalBlock:
    operator: str
    events: List[Union[Event, Dict[str, Any]]] = field(default_factory=list)
    interval: Optional[List[int]] = None
    _token: object = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if self._token is not TOKEN:
            raise TypeError(
                "Do not instantiate TemporalBlock directly. "
                "Use CohortDefinition.logic.AND/OR/BEFORE/NOT instead."
            )
        _assert_operator_arity_or_raise(self.operator, len(self.events))

    def to_yaml(self) -> Dict[str, Any]:
        """Return the temporal block as a YAML-ready dict."""
        _assert_operator_arity_or_raise(self.operator, len(self.events))
        block: Dict[str, Any] = {"operator": SingleQuoted(self.operator)}
        if self.interval is not None:
            block["interval"] = FlowList(self.interval)
        evs = []
        for e in self.events:
            evs.append(e.to_yaml_event() if isinstance(e, Event) else e)
        block["events"] = evs
        return block

# ---------- CohortCriteria (renamed from CohortCriteria) ----------
@dataclass
class CohortCriteria:
    """
    High-level cohort definition container.
    Users compose Events and logical operators, without touching YAML directly.
    """
    temporal_blocks: Optional[List[Union[Dict[str, Any], Event, "TemporalBlock"]]] = None
    demographics: Optional[Demographics] = None

    # Optional exclusion (to emit exclusion_criteria in the YAML)
    exclusion_blocks: Optional[List[Union[Dict[str, Any], Event, "TemporalBlock"]]] = None
    exclusion_demographics: Optional[Demographics] = None

    # ----------------- Public UX: print() shows YAML -----------------
    def __str__(self) -> str:
        """Pretty string form: YAML."""
        return self._to_yaml(sort_keys=False)

    def __repr__(self) -> str:
        """REPL-friendly representation: YAML."""
        return self.__str__()

    # ----------------- Internal build helpers -----------------
    def _build_temporal_section(self, blocks: List[Union[Event, Dict[str, Any], "TemporalBlock"]]) -> List[Dict[str, Any]]:
        """
        Normalize a list of temporal blocks to a 'temporal_events' array:
        - 0 blocks  -> []
        - 1 block   -> emit as-is if it already has 'operator'; else wrap with top-level AND
        - >=2 blocks-> emit as PARALLEL groups (NO extra top-level AND wrapper)
        """
        normalized = [_as_yaml(x) for x in blocks if x is not None]
        if not normalized:
            return []
        if len(normalized) == 1:
            item = normalized[0]
            if isinstance(item, dict) and "operator" in item:
                return [item]
            return [{"operator": SingleQuoted("AND"), "events": [item]}]
        return normalized

    def to_dict(self) -> Dict[str, Any]:
        """Materialize the full cohort definition as a plain Python dict."""
        out: Dict[str, Any] = {"inclusion_criteria": {}}
        ic = out["inclusion_criteria"]

        if self.demographics:
            demo = self.demographics.to_yaml()
            if demo:
                ic["demographics"] = demo

        if self.temporal_blocks:
            inc_te = self._build_temporal_section(self.temporal_blocks)
            if inc_te:
                ic["temporal_events"] = inc_te

        if self.exclusion_demographics or self.exclusion_blocks:
            exc: Dict[str, Any] = {}
            if self.exclusion_demographics:
                ed = self.exclusion_demographics.to_yaml()
                if ed:
                    exc["demographics"] = ed
            if self.exclusion_blocks:
                exc_te = self._build_temporal_section(self.exclusion_blocks)
                if exc_te:
                    exc["temporal_events"] = exc_te
            if exc:
                out["exclusion_criteria"] = exc

        return out

    # ----------------- Internal YAML emitter (hidden from users) -----------------
    def _to_yaml(self, sort_keys: bool = False) -> str:
        """
        INTERNAL: Convert cohort definition to a YAML string.
        Users should not call this directly; printing the object is recommended.
        """
        return yaml.dump(
            self.to_dict(),
            sort_keys=sort_keys,
            allow_unicode=True,
            indent=2,
            default_flow_style=False,
        )

    # ----------------- Public save API -----------------
    def save(self, path: Union[str, Path]) -> Path:
        """Save the cohort YAML to disk."""
        p = Path(path)
        p.write_text(self._to_yaml(sort_keys=False), encoding="utf-8")
        return p

    # ----------------- Backward-compat shims -----------------
    def to_yaml(self, sort_keys: bool = False, as_object: bool = False):
        """
        DEPRECATED: kept for backward compatibility.
        Returns YAML string (or dict if as_object=True).
        """
        yaml_str = self._to_yaml(sort_keys=sort_keys)
        if as_object:
            return yaml.safe_load(yaml_str)
        return yaml_str

    def save_yaml(self, path: Union[str, Path]) -> Path:
        """DEPRECATED: use .save(path) instead."""
        return self.save(path)
    
    # Track a lazily-created temp YAML path for this instance (hidden from users)
    _tmp_yaml_path: Optional[str] = field(default=None, repr=False, compare=False)
    _tmp_finalizer: Optional[weakref.finalize] = field(default=None, repr=False, compare=False)

    # ----------------- INTERNAL: ensure a temp .yaml exists for path-based APIs -----------------
    def _ensure_temp_yaml_file(self, overwrite: bool = True) -> str:
        """
        Create (or refresh) a temporary .yaml file that mirrors the CURRENT cohort definition.
        This lets external libraries that only accept a YAML *file path* consume this object
        directly without exposing YAML to end users.
        """
        # Create a new temp file if none exists
        if not self._tmp_yaml_path:
            fd, path = tempfile.mkstemp(prefix="cohort_", suffix=".yaml")
            os.close(fd)  # we will reopen with text mode
            self._tmp_yaml_path = path
            _TEMP_YAML_PATHS.add(path)

            # Register object-finalizer to auto-delete when this cohort is GC'd
            self._tmp_finalizer = weakref.finalize(self, self._cleanup_temp_yaml_silent, path)

        # (Re)write the latest YAML into the temp file if requested
        if overwrite and self._tmp_yaml_path:
            try:
                with open(self._tmp_yaml_path, "w", encoding="utf-8") as f:
                    f.write(self._to_yaml(sort_keys=False))
            except Exception:
                # If anything goes wrong, fall back to creating a fresh file
                fd, path = tempfile.mkstemp(prefix="cohort_", suffix=".yaml")
                os.close(fd)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._to_yaml(sort_keys=False))
                # update registry
                if self._tmp_yaml_path:
                    _TEMP_YAML_PATHS.discard(self._tmp_yaml_path)
                self._tmp_yaml_path = path
                _TEMP_YAML_PATHS.add(path)
                self._tmp_finalizer = weakref.finalize(self, self._cleanup_temp_yaml_silent, path)

        return self._tmp_yaml_path

    @staticmethod
    def _cleanup_temp_yaml_silent(path: str) -> None:
        """Internal: silent best-effort delete for a single temp file."""
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        finally:
            _TEMP_YAML_PATHS.discard(path)

    # ----------------- PATH-LIKE SURFACE: make the object behave like a YAML path -----------------
    def __fspath__(self) -> str:
        """
        Allow `open(cohort)` / `os.fspath(cohort)` to work by returning a real temp .yaml path.
        """
        return self._ensure_temp_yaml_file(overwrite=True)

    def endswith(self, suffix: str) -> bool:
        """
        Some external APIs branch on `.endswith('.yaml')`. We proxy that to the temp path.
        """
        return self._ensure_temp_yaml_file(overwrite=False).endswith(suffix)
