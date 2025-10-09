"""
logic.py
High-level logical helpers for building cohort queries.

- AND(*ops) -> TemporalBlock
- OR(*ops)  -> TemporalBlock
- BEFORE(a, b, b_offset=None) -> dict
- AFTER(a, b, a_offset=None)  -> dict // currently not implemented
"""

from typing import Union, Optional
from python_to_YAML.builder import TemporalBlock, TOKEN, SingleQuoted
from python_to_YAML.events import Event

Operand = Union[Event, TemporalBlock, dict]

def _as_yaml(x: Operand) -> dict:
    """Normalize one operand to a plain YAML dict."""
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


# AND & OR
def AND(a: Operand, b: Operand) -> TemporalBlock:
    """Conjunction (strictly 2 operands)."""
    _require_exact_arity("AND", 2, 2)
    a_yaml = _as_yaml(a)
    b_yaml = _as_yaml(b)
    # Pack two YAML operands into a TemporalBlock (token-gated)
    return TemporalBlock(operator="AND", events=[a_yaml, b_yaml], _token=TOKEN)


def OR(a: Operand, b: Operand) -> TemporalBlock:
    """Disjunction (strictly 2 operands)."""
    _require_exact_arity("OR", 2, 2)
    a_yaml = _as_yaml(a)
    b_yaml = _as_yaml(b)
    return TemporalBlock(operator="OR", events=[a_yaml, b_yaml], _token=TOKEN)


# BEFORE
def BEFORE(a: Operand, b: Operand, b_offset: Optional[int] = None) -> dict:
    """
    'a BEFORE b' (strictly 2 operands).
    If b_offset is provided, attach it to the second event as `offset: <b_offset>`.
    """
    _require_exact_arity("BEFORE", 2, 2)
    left = _as_yaml(a)
    right = _as_yaml(b)
    if b_offset is not None:
        right = {**right, "offset": int(b_offset)}
    return {"operator": SingleQuoted("BEFORE"), "events": [left, right]}


# NOT
def NOT(x: Operand) -> dict:
    """Negation (strictly 1 operand)."""
    _require_exact_arity("NOT", 1, 1)
    x_yaml = _as_yaml(x)
    return {"operator": SingleQuoted("NOT"), "events": [x_yaml]}