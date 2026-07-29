from __future__ import annotations

import math
from typing import Any

from tools._shared import err

def evaluate_expression(expression: str = "") -> dict[str, Any]:
    try:
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return {"tool": "evaluate_expression", "expression": expression, "result": result}
    except Exception as exc:
        return err("evaluate_expression", exc)
