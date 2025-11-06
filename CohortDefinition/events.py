from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Any
import yaml
import csv
from pathlib import Path

# Default lightweight OHDSI→SNOMED mapping shipped with the package
_SNOMED_MAP_FILE = Path(__file__).resolve().parent / "data" / "ohdsi_to_snomed_map.csv"
_OHDSI_TO_SNOMED: Dict[int, str] = {}

# Load the mapping once at import time (best-effort)
# CSV is expected to have at least two columns:
#   - "ohdsi_concept_id": OMOP / OHDSI concept_id (int-like)
#   - "snomed_code":      corresponding SNOMED code (string / int-like)
if _SNOMED_MAP_FILE.exists():
    with open(_SNOMED_MAP_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ohdsi = int(row["ohdsi_concept_id"])
                snomed = str(row["snomed_code"]).strip()
                _OHDSI_TO_SNOMED[ohdsi] = snomed
            except Exception:
                # Skip malformed rows quietly
                continue


class SingleQuoted(str):
    pass


def _single_quoted_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")


yaml.add_representer(SingleQuoted, _single_quoted_str_representer)


class Event:
    """Abstract base; concrete events below map 1:1 to YAML event_type values."""

    def to_yaml_event(self) -> Dict[str, Any]:
        raise NotImplementedError

    def _resolve_concept(self, id_value, id_type: str, domain: str) -> int:
        """
        Resolve user input into a *SNOMED* concept code (numeric).

        - id_type='SNOMED' (default) → passthrough (we assume caller already
          supplied a SNOMED concept code that OMOP uses in the CDM tables).
        - id_type='OHDSI' / 'OMOP' / 'CONCEPT' → look up the OHDSI→SNOMED
          mapping table (using ohdsi_concept_id as key).
        """
        id_type_upper = (id_type or "SNOMED").upper()

        # SNOMED (default, already in the right coding system for OMOP Condition)
        if id_type_upper in ("SNOMED", "SNOMEDCT", "SNOMED_CT", "SNOMED-CT"):
            return int(id_value)

        # OHDSI / OMOP concept_id → map to SNOMED code
        if id_type_upper in ("OHDSI", "OMOP", "CONCEPT"):
            key = int(id_value)
            if key in _OHDSI_TO_SNOMED:
                # SNOMED codes are usually numeric strings; cast back to int for YAML
                return int(_OHDSI_TO_SNOMED[key])
            raise ValueError(
                f"OHDSI concept_id {id_value} not found in built-in OHDSI→SNOMED "
                "mapping. Please extend CohortDefinition/data/snomed_to_ohdsi_map.csv "
                "or register a mapping at runtime."
            )

        raise ValueError(
            f"Unsupported id_type={id_type!r}. Use 'SNOMED' (default) or 'OHDSI'."
        )


# ---------------- ConditionOccurrence ----------------
@dataclass
class ConditionOccurrence(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None  # when schema uses "at least N occurrences"
    offset: Optional[int] = None
    id_type: Optional[str] = None  # 'SNOMED' (default) or 'OHDSI'

    def to_yaml_event(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"event_type": SingleQuoted("condition_occurrence")}
        if self.event_concept_id is not None:
            # Resolve to SNOMED if id_type is OHDSI; otherwise pass through
            cid = (
                self.event_concept_id
                if not self.id_type
                else self._resolve_concept(
                    self.event_concept_id, self.id_type, domain="condition_occurrence"
                )
            )
            d["event_concept_id"] = int(cid)
        if self.code_type is not None:
            d["code_type"] = self.code_type
        if self.code is not None:
            d["code"] = self.code
        if self.event_instance is not None:
            d["event_instance"] = self.event_instance
        if self.offset is not None:
            d["offset"] = int(self.offset)
        return d


# ---------------- DrugExposure ----------------
@dataclass
class DrugExposure(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None
    offset: Optional[int] = None
    id_type: Optional[str] = None  # 'SNOMED' (default) or 'OHDSI'

    def to_yaml_event(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"event_type": SingleQuoted("drug_exposure")}
        if self.event_concept_id is not None:
            cid = (
                self.event_concept_id
                if not self.id_type
                else self._resolve_concept(
                    self.event_concept_id, self.id_type, domain="drug_exposure"
                )
            )
            d["event_concept_id"] = int(cid)
        if self.code_type is not None:
            d["code_type"] = self.code_type
        if self.code is not None:
            d["code"] = self.code
        if self.event_instance is not None:
            d["event_instance"] = self.event_instance
        if self.offset is not None:
            d["offset"] = int(self.offset)
        return d


# ------------- ProcedureOccurrence -------------
@dataclass
class ProcedureOccurrence(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None
    offset: Optional[int] = None
    id_type: Optional[str] = None  # 'SNOMED' (default) or 'OHDSI'

    def to_yaml_event(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"event_type": SingleQuoted("procedure_occurrence")}
        if self.event_concept_id is not None:
            cid = (
                self.event_concept_id
                if not self.id_type
                else self._resolve_concept(
                    self.event_concept_id,
                    self.id_type,
                    domain="procedure_occurrence",
                )
            )
            d["event_concept_id"] = int(cid)
        if self.code_type is not None:
            d["code_type"] = self.code_type
        if self.code is not None:
            d["code"] = self.code
        if self.event_instance is not None:
            d["event_instance"] = self.event_instance
        if self.offset is not None:
            d["offset"] = int(self.offset)
        return d


# ----------------- Measurement -----------------
@dataclass
class Measurement(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None
    value_filter: Optional[Dict[str, Any]] = None
    offset: Optional[int] = None
    id_type: Optional[str] = None  # 'SNOMED' (default) or 'OHDSI'

    def to_yaml_event(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"event_type": SingleQuoted("measurement")}
        if self.event_concept_id is not None:
            cid = (
                self.event_concept_id
                if not self.id_type
                else self._resolve_concept(
                    self.event_concept_id, self.id_type, domain="measurement"
                )
            )
            d["event_concept_id"] = int(cid)
        if self.code_type is not None:
            d["code_type"] = self.code_type
        if self.code is not None:
            d["code"] = self.code
        if self.event_instance is not None:
            d["event_instance"] = self.event_instance
        if self.value_filter is not None:
            d["value_filter"] = self.value_filter
        if self.offset is not None:
            d["offset"] = int(self.offset)
        return d


# --------------- VisitOccurrence ---------------
@dataclass
class VisitOccurrence(Event):
    event_concept_id: Optional[Union[int, str]] = None  # e.g., 9201 inpatient
    qualifiers: Optional[Dict[str, Any]] = None  # optional, if schema allows
    event_instance: Optional[int] = None
    offset: Optional[int] = None
    id_type: Optional[str] = None  # 'SNOMED' (default) or 'OHDSI'

    def to_yaml_event(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"event_type": SingleQuoted("visit_occurrence")}
        if self.event_concept_id is not None:
            cid = (
                self.event_concept_id
                if not self.id_type
                else self._resolve_concept(
                    self.event_concept_id, self.id_type, domain="visit_occurrence"
                )
            )
            d["event_concept_id"] = int(cid)
        if self.qualifiers is not None:
            d["qualifiers"] = self.qualifiers
        if self.event_instance is not None:
            d["event_instance"] = self.event_instance
        if self.offset is not None:
            d["offset"] = int(self.offset)
        return d


# --------------- DateEvent ---------------
@dataclass
class DateEvent(Event):
    timestamp: str  # 'YYYY-MM-DD'

    def to_yaml_event(self) -> Dict[str, Any]:
        return {"event_type": "date", "timestamp": self.timestamp}
