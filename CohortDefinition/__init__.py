# __init__.py
__all__ = [
    "ConditionOccurrence","DrugExposure","ProcedureOccurrence",
    "Measurement","VisitOccurrence","DateEvent",
    "Demographics","CohortCriteria",
    "AND","OR","BEFORE","NOT"
]

def __getattr__(name):
    # events.py
    if name in {
        "ConditionOccurrence","DrugExposure","ProcedureOccurrence",
        "Measurement","VisitOccurrence","DateEvent"
    }:
        from . import events as _events
        return getattr(_events, name)

    # builder.py
    if name in {"Demographics","CohortCriteria"}:
        from . import builder as _builder
        return getattr(_builder, name)

    # Backward-compat: map old name to new class
    if name == "CohortCriteria":
        from .builder import CohortCriteria as _Compat
        return _Compat

    # logic.py
    if name in {"AND","OR","BEFORE","NOT"}:
        from . import logic as _logic
        return getattr(_logic, name)

    raise AttributeError(f"module 'BiasAnalyzerYAMLBuilder' has no attribute '{name}'")
