__all__ = [
    "ConditionOccurrence","DrugExposure","ProcedureOccurrence",
    "Measurement","VisitOccurrence","DateEvent",
    "Demographics","CohortYAML",
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
    if name in {"Demographics","CohortYAML"}:
        from . import builder as _builder
        return getattr(_builder, name)

    # logic.py（AND/OR/BEFORE)
    if name in {"AND","OR","BEFORE","AFTER"}:
        from . import logic as _logic
        return getattr(_logic, name)

    raise AttributeError(f"module 'BiasAnalyzerYAMLBuilder' has no attribute '{name}'")