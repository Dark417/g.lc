"""Plain Python functions the model can call.

ADK turns a function into a tool from its signature and docstring: the docstring is what the
model reads to decide when to call it, and the type hints become the JSON schema. Return a dict
so the model gets labelled fields, and report errors in the dict instead of raising.
"""

import ast
import operator
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_current_time(timezone: str) -> dict:
    """Get the current date and time in an IANA timezone, e.g. "Europe/Berlin" or "UTC".

    Args:
        timezone: IANA timezone name. Use "UTC" if the user did not specify one.
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return {"status": "error", "message": f"unknown timezone: {timezone}"}
    return {
        "status": "ok",
        "timezone": timezone,
        "iso": now.isoformat(),
        "weekday": now.strftime("%A"),
    }


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval(node: ast.AST) -> float:
    # A tiny AST walker: numbers and + - * / ** % only. Never eval() model output.
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    raise ValueError("unsupported expression")


def calculate(expression: str) -> dict:
    """Evaluate an arithmetic expression exactly. Use this for any math instead of guessing.

    Args:
        expression: Arithmetic using numbers and + - * / ** % and parentheses, e.g. "12 * (3 + 4)".
    """
    try:
        value = _eval(ast.parse(expression, mode="eval").body)
    except (ValueError, SyntaxError, ZeroDivisionError, TypeError) as e:
        return {"status": "error", "message": f"cannot evaluate {expression!r}: {e}"}
    return {"status": "ok", "expression": expression, "result": value}
