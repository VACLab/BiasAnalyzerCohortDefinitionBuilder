# logic.py
"""
High-level logical helpers for building cohort queries.

Users compose queries with functions (no direct YAML manipulation):
- AND(a, b)     -> TemporalBlock
- OR(a, b)      -> TemporalBlock
- BEFORE(a, b)  -> dict (operator block)
- NOT(x)        -> dict (operator block)
"""

from typing import Union, Optional
from CohortDefinition.builder import TemporalBlock, TOKEN, SingleQuoted
from CohortDefinition.events import Event

Operand = Union[Event, TemporalBlock, dict]

def _as_yaml(x: Operand) -> dict:
    """Normalize operand to a YAML-ready dict."""
    if isinstance(x, Event):
        return x.to_yaml_event()
    if isinstance(x, TemporalBlock):
        return x.to_yaml()
    if isinstance(x, dict):
        return x
    raise TypeError(f"Unsupported operand type: {type(x)}")

def _require_exact_arity(fn_name: str, got: int, expected: int) -> None:
    """Raise a consistent ValueError on wrong arity."""
    if got != expected:
        raise ValueError(f"{fn_name}() requires exactly {expected} operand(s), got {got}.")

def AND(*ops: Operand) -> TemporalBlock:
    """Binary conjunction (exactly 2 operands)."""
    _require_exact_arity("AND", len(ops), 2)
    a_yaml = _as_yaml(ops[0])
    b_yaml = _as_yaml(ops[1])
    return TemporalBlock(operator="AND", events=[a_yaml, b_yaml], _token=TOKEN)

def OR(*ops: Operand) -> TemporalBlock:
    """Binary disjunction (exactly 2 operands)."""
    _require_exact_arity("OR", len(ops), 2)
    a_yaml = _as_yaml(ops[0])
    b_yaml = _as_yaml(ops[1])
    return TemporalBlock(operator="OR", events=[a_yaml, b_yaml], _token=TOKEN)

def BEFORE(a: Operand, b: Operand, offset: Optional[int] = None) -> dict:
    """
    'a BEFORE b' (exactly 2 operands).
    If `offset` is provided, it is attached to the second event as `offset: <int>`.
    """
    _require_exact_arity("BEFORE", 2, 2)  # consistent runtime check
    a_yaml = _as_yaml(a)
    b_yaml = _as_yaml(b)
    if offset is not None:
        b_yaml = {**b_yaml, "offset": int(offset)}
    return {"operator": SingleQuoted("BEFORE"), "events": [a_yaml, b_yaml]}

def NOT(x: Operand, *rest: Operand) -> dict:
    """Unary negation (exactly 1 operand)."""
    if rest:
        _require_exact_arity("NOT", 1 + len(rest), 1)
    x_yaml = _as_yaml(x)
    return {"operator": SingleQuoted("NOT"), "events": [x_yaml]}
