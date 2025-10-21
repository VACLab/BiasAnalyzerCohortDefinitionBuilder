
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
import yaml

from python_to_YAML.events import Event

'''@dataclass
class Demographics:
    gender: Optional[str] = None
    min_birth_year: Optional[int] = None
    max_birth_year: Optional[int] = None

    def to_yaml(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.gender: d["gender"] = self.gender
        if self.min_birth_year is not None: d["min_birth_year"] = int(self.min_birth_year)
        if self.max_birth_year is not None: d["max_birth_year"] = int(self.max_birth_year)
        return d
        '''

class _Token:
    pass

TOKEN = _Token()
    
@dataclass
class Demographics:
    gender: Optional[str] = None
    min_birth_year: Optional[int] = None
    max_birth_year: Optional[int] = None
    '''race: Optional[str] = None
    ethnicity: Optional[str] = None'''

    def to_yaml(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.gender:
            d["gender"] = SingleQuoted(self.gender)
        if self.min_birth_year is not None:
            d["min_birth_year"] = int(self.min_birth_year)
        if self.max_birth_year is not None:
            d["max_birth_year"] = int(self.max_birth_year)
        '''if self.race:
            d["race"] = SingleQuoted(self.race)
        if self.ethnicity:
            d["ethnicity"] = SingleQuoted(self.ethnicity)'''
        return d

def _as_yaml(x: Union[Event, Dict[str, Any], "TemporalBlock"]) -> Dict[str, Any]:
    """
    Convert a supported operand (Event | TemporalBlock | dict) to a plain YAML dict.
    - Event -> .to_yaml_event()
    - TemporalBlock -> .to_yaml()
    - dict -> as is
    """
    # NOTE: import here to avoid circular imports at module load time
    from .builder import TemporalBlock as _TB  # type: ignore
    if isinstance(x, Event):
        return x.to_yaml_event()
    if isinstance(x, dict):
        return x
    if isinstance(x, _TB):
        return x.to_yaml()
    raise TypeError(f"Unsupported temporal block element: {type(x)}")

'''@dataclass
class TemporalBlock:
    operator: str  # 'AND' | 'OR' | 'NOT' | 'BEFORE' | 'AFTER'
    events: List[Union[Event, Dict[str, Any]]] = field(default_factory=list)
    interval: Optional[List[int]] = None

    def to_yaml(self) -> Dict[str, Any]:
        block: Dict[str, Any] = {"operator": self.operator}
        if self.interval is not None:
            block["interval"] = FlowList(self.interval)   # FlowList
        evs = []
        for e in self.events:
            evs.append(e.to_yaml_event() if isinstance(e, Event) else e)
        block["events"] = evs
        return block
        '''
    
@dataclass
class TemporalBlock:
    operator: str # 'AND' | 'OR' | 'NOT' | 'BEFORE' | 'AFTER'
    events: List[Union[Event, Dict[str, Any]]] = field(default_factory=list)
    interval: Optional[List[int]] = None
    _token: object = field(default=None, repr=False, compare=False)

    def __post_init__(self):

        if self._token is not TOKEN:
            raise TypeError(
                "Do not instantiate TemporalBlock directly. "
                "Use python_to_YAML.logic.AND(...) or OR(...) instead."
            )

    def to_yaml(self) -> Dict[str, Any]:

        block: Dict[str, Any] = {"operator": SingleQuoted(self.operator)}
        if self.interval is not None:
            block["interval"] = FlowList(self.interval)
        evs = []
        for e in self.events:
            evs.append(e.to_yaml_event() if isinstance(e, Event) else e)
        block["events"] = evs
        return block


class FlowList(list):
    """Force flow style for lists like interval."""
    pass

def flow_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(FlowList, flow_list_representer)

class FlowList(list):
    """Force flow style for specific lists (e.g., interval)."""
    pass

def _flow_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(FlowList, _flow_list_representer)

class SingleQuoted(str):
    """Mark a string value to be emitted with single quotes."""
    pass

def _single_quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

yaml.add_representer(SingleQuoted, _single_quoted_str_representer)

@dataclass
class CohortYAML:
    temporal_blocks: Optional[List[Union[Dict[str, Any], Event, "TemporalBlock"]]] = None
    demographics: Optional[Demographics] = None

    # NEW: exclusion side (mirrors inclusion temporal blocks)
    exclusion_blocks: Optional[List[Union[Dict[str, Any], Event, "TemporalBlock"]]] = None

    def _build_temporal_section(self, blocks: List[Union[Event, Dict[str, Any], "TemporalBlock"]]) -> List[Dict[str, Any]]:
        """
        Build a normalized 'temporal_events' list following the existing rules:
          - 0 blocks  -> []
          - 1 block   -> if it already has 'operator', emit as-is; else wrap with top-level AND
          - >=2 blocks-> wrap with top-level AND containing all blocks
        """
        normalized = [_as_yaml(x) for x in blocks if x is not None]
        if not normalized:
            return []
        if len(normalized) == 1:
            item = normalized[0]
            if isinstance(item, dict) and "operator" in item:
                return [item]
            return [{"operator": SingleQuoted("AND"), "events": [item]}]
        return [{"operator": SingleQuoted("AND"), "events": normalized}]

    def to_dict(self) -> Dict[str, Any]:
        """
        Keep existing inclusion behavior; add 'exclusion_criteria' if provided.
        """
        out: Dict[str, Any] = {"inclusion_criteria": {}}
        ic = out["inclusion_criteria"]

        # 1) demographics first (unchanged)
        if self.demographics:
            demo = self.demographics.to_yaml()
            if demo:
                ic["demographics"] = demo

        # 2) inclusion temporal_events (unchanged behavior)
        if self.temporal_blocks:
            inc_ts = self._build_temporal_section(self.temporal_blocks)
            if inc_ts:
                ic["temporal_events"] = inc_ts

        # 3) exclusion criteria: temporal_events only (for now)
        if self.exclusion_blocks:
            exc_ts = self._build_temporal_section(self.exclusion_blocks)
            if exc_ts:
                out["exclusion_criteria"] = {"temporal_events": exc_ts}

        return out

    def save_yaml(self, path: Union[str, Path]) -> Path:
        p = Path(path)
        p.write_text(yaml.dump(self.to_dict(),
                               sort_keys=False,
                               allow_unicode=True,
                               indent=2,
                               default_flow_style=False))
        return p