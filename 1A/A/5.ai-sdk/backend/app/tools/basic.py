"""Pure local tools. Typed signature + Google-style docstring = the tool schema in every framework."""

import ast
import math
import operator
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_BIN = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}  # fmt: skip
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "exp": math.exp,
    "abs": abs, "round": round, "min": min, "max": max,
}  # fmt: skip
_CONSTS = {"pi": math.pi, "e": math.e}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")
        return _BIN[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError(f"unsupported expression: {ast.dump(node)[:60]}")


def evaluate(expression: str) -> float:
    """Safe arithmetic: an AST whitelist, never eval()."""
    return _eval(ast.parse(expression.replace("^", "**"), mode="eval"))


async def calculator(expression: str) -> dict:
    """Evaluate an arithmetic expression exactly. Use it for any math instead of mental arithmetic.

    Args:
        expression: Python-style arithmetic, e.g. "0.17 * 2340" or "sqrt(2) * (3 + 4)".
            Supports + - * / // % **, parentheses, sqrt, log, log10, exp, abs, round, min, max, pi, e.
    """
    try:
        value = evaluate(expression)
    except Exception as e:  # report to the model, which can retry with a fixed expression
        return {"status": "error", "error": str(e)}
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    elif isinstance(value, float):
        value = round(value, 10)
    return {"status": "ok", "expression": expression, "result": value}


async def current_time(timezone: str) -> dict:
    """Get the current date and time in a timezone.

    Args:
        timezone: IANA timezone name, e.g. "UTC", "Europe/Paris", "America/New_York".
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
    except (ZoneInfoNotFoundError, ValueError):
        return {"status": "error", "error": f"unknown timezone {timezone!r}"}
    return {"status": "ok", "timezone": timezone, "iso": now.isoformat(timespec="seconds")}
