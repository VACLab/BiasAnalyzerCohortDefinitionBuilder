from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Any
import yaml

class SingleQuoted(str):
    pass

def _single_quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

yaml.add_representer(SingleQuoted, _single_quoted_str_representer)


class Event:
    """Abstract base; concrete events below map 1:1 to YAML event_type values."""
    def to_yaml_event(self) -> Dict[str, Any]:
        raise NotImplementedError

@dataclass
class ConditionOccurrence(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None  # when schema uses "at least N occurrences"
    offset: Optional[int] = None
    def to_yaml_event(self) -> Dict[str, Any]:
        d = {"event_type": SingleQuoted("condition_occurrence")}
        if self.event_concept_id is not None: d["event_concept_id"] = self.event_concept_id
        if self.code_type is not None: d["code_type"] = self.code_type
        if self.code is not None: d["code"] = self.code
        if self.event_instance is not None: d["event_instance"] = self.event_instance
        if self.offset is not None: d["offset"] = int(self.offset)
        return d

@dataclass
class DrugExposure(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None
    offset: Optional[int] = None
    def to_yaml_event(self) -> Dict[str, Any]:
        d = {"event_type": SingleQuoted("drug_exposure")}
        if self.event_concept_id is not None: d["event_concept_id"] = self.event_concept_id
        if self.code_type is not None: d["code_type"] = self.code_type
        if self.code is not None: d["code"] = self.code
        if self.event_instance is not None: d["event_instance"] = self.event_instance
        if self.offset is not None: d["offset"] = int(self.offset)
        return d

@dataclass
class ProcedureOccurrence(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None
    offset: Optional[int] = None
    def to_yaml_event(self) -> Dict[str, Any]:
        d = {"event_type": SingleQuoted("procedure_occurrence")}
        if self.event_concept_id is not None: d["event_concept_id"] = self.event_concept_id
        if self.code_type is not None: d["code_type"] = self.code_type
        if self.code is not None: d["code"] = self.code
        if self.event_instance is not None: d["event_instance"] = self.event_instance
        if self.offset is not None: d["offset"] = int(self.offset)
        return d

@dataclass
class E(Event):
    event_concept_id: Optional[Union[int, str]] = None
    code_type: Optional[str] = None
    code: Optional[Union[str, List[str]]] = None
    event_instance: Optional[int] = None
    value_filter: Optional[Dict[str, Any]] = None
    offset: Optional[int] = None
    def to_yaml_event(self) -> Dict[str, Any]:
        d = {"event_type": SingleQuoted("measurement")}
        if self.event_concept_id is not None: d["event_concept_id"] = self.event_concept_id
        if self.code_type is not None: d["code_type"] = self.code_type
        if self.code is not None: d["code"] = self.code
        if self.event_instance is not None: d["event_instance"] = self.event_instance
        if self.value_filter is not None: d["value_filter"] = self.value_filter
        if self.offset is not None: d["offset"] = int(self.offset)
        return d

@dataclass
class VisitOccurrence(Event):
    event_concept_id: Optional[Union[int, str]] = None  # e.g., 9201 inpatient
    qualifiers: Optional[Dict[str, Any]] = None        # optional, if schema allows
    event_instance: Optional[int] = None
    offset: Optional[int] = None
    def to_yaml_event(self) -> Dict[str, Any]:
        d = {"event_type": SingleQuoted("visit_occurrence")}
        if self.event_concept_id is not None: d["event_concept_id"] = self.event_concept_id
        if self.qualifiers is not None: d["qualifiers"] = self.qualifiers
        if self.event_instance is not None: d["event_instance"] = self.event_instance
        if self.offset is not None: d["offset"] = int(self.offset)
        return d

@dataclass
class DateEvent(Event):
    timestamp: str  # 'YYYY-MM-DD'
    def to_yaml_event(self) -> Dict[str, Any]:
        return {"event_type": "date", "timestamp": self.timestamp}
