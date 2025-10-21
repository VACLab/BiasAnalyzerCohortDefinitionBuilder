"""
logic.py
High-level logical helpers for building cohort queries.

- AND(*ops) -> TemporalBlock
- OR(*ops)  -> TemporalBlock
- BEFORE(a, b, b_offset=None) -> dict
- AFTER(a, b, a_offset=None)  -> dict // currently not implemented
"""

from typing import Union, Optional, Iterable, Tuple
from python_to_YAML.builder import TemporalBlock, TOKEN, SingleQuoted
from python_to_YAML.events import Event

Operand = Union[Event, TemporalBlock, dict]

def _as_yaml(x: Operand) -> dict:
    if isinstance(x, Event):
        return x.to_yaml_event()
    if isinstance(x, TemporalBlock):
        return x.to_yaml()
    if isinstance(x, dict):
        return x
    raise TypeError(f"Unsupported operand type: {type(x)}")

def _require_exact_arity(fn_name: str, got: int, expected: int) -> None:
    if got != expected:
        raise ValueError(f"{fn_name}() requires exactly {expected} operand(s), got {got}.")

# ---------- Strict-arity operators ----------

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
    If `offset` is provided, attach to the second event as `offset: <int>`.
    """
    _require_exact_arity("BEFORE", 2, 2)  # signature enforces 2, keep runtime check for consistency
    a_yaml = _as_yaml(a)
    b_yaml = _as_yaml(b)
    if offset is not None:
        b_yaml = {**b_yaml, "offset": int(offset)}
    return {"operator": SingleQuoted("BEFORE"), "events": [a_yaml, b_yaml]}

def NOT(x: Operand, *rest: Operand) -> dict:
    """Unary negation (exactly 1 operand)."""
    # If users mistakenly pass extra operands, surface a consistent ValueError
    if rest:
        _require_exact_arity("NOT", 1 + len(rest), 1)
    x_yaml = _as_yaml(x)
    return {"operator": SingleQuoted("NOT"), "events": [x_yaml]}
