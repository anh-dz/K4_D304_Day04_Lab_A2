from __future__ import annotations

import ast
import math
import operator
from typing import Any, Callable

from tools._shared import err


MAX_EXPRESSION_LENGTH = 300
MAX_AST_NODES = 80
MAX_ABS_RESULT = 10**100

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_MATH_FUNCTIONS: dict[str, Callable[..., Any]] = {
    name: getattr(math, name)
    for name in (
        "acos",
        "asin",
        "atan",
        "atan2",
        "ceil",
        "cos",
        "degrees",
        "exp",
        "fabs",
        "floor",
        "hypot",
        "log",
        "log10",
        "log2",
        "pow",
        "radians",
        "sin",
        "sqrt",
        "tan",
        "trunc",
    )
}

_MATH_CONSTANTS: dict[str, float] = {
    "e": math.e,
    "pi": math.pi,
    "tau": math.tau,
}


class SafeMathEvaluator(ast.NodeVisitor):
    """Evaluate a deliberately small subset of Python numeric expressions."""

    def visit_Expression(self, node: ast.Expression) -> int | float:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> int | float:
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Only numeric literals are allowed")
        self._validate_result(value)
        return value

    def visit_BinOp(self, node: ast.BinOp) -> int | float:
        operation = _BINARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError(f"Operator {type(node.op).__name__} is not allowed")

        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large")

        result = operation(left, right)
        self._validate_result(result)
        return result

    def visit_UnaryOp(self, node: ast.UnaryOp) -> int | float:
        operation = _UNARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError(f"Unary operator {type(node.op).__name__} is not allowed")
        result = operation(self.visit(node.operand))
        self._validate_result(result)
        return result

    def visit_Name(self, node: ast.Name) -> float:
        if node.id in _MATH_CONSTANTS:
            return _MATH_CONSTANTS[node.id]
        raise ValueError(f"Unknown name: {node.id}")

    def visit_Attribute(self, node: ast.Attribute) -> float:
        if isinstance(node.value, ast.Name) and node.value.id == "math" and node.attr in _MATH_CONSTANTS:
            return _MATH_CONSTANTS[node.attr]
        raise ValueError("Only approved math constants are allowed")

    def visit_Call(self, node: ast.Call) -> int | float:
        if node.keywords:
            raise ValueError("Keyword arguments are not allowed")
        if len(node.args) > 8:
            raise ValueError("Too many function arguments")

        function_name: str | None = None
        if isinstance(node.func, ast.Name):
            function_name = node.func.id
        elif (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "math"
        ):
            function_name = node.func.attr

        function = _MATH_FUNCTIONS.get(function_name or "")
        if function is None:
            raise ValueError("Only approved math functions are allowed")

        result = function(*(self.visit(argument) for argument in node.args))
        self._validate_result(result)
        return result

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Expression element {type(node).__name__} is not allowed")

    @staticmethod
    def _validate_result(value: Any) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("The result must be a real number")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("The result must be finite")
        if abs(value) > MAX_ABS_RESULT:
            raise ValueError("The result is too large")


def evaluate_expression(expression: str = "") -> dict[str, Any]:
    normalized = expression.strip()
    try:
        if not normalized:
            raise ValueError("expression is required")
        if len(normalized) > MAX_EXPRESSION_LENGTH:
            raise ValueError("expression is too long")

        tree = ast.parse(normalized, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
            raise ValueError("expression is too complex")

        result = SafeMathEvaluator().visit(tree)
        return {"tool": "calculator", "expression": normalized, "result": result, "error": None}
    except Exception as exc:
        return err("calculator", exc)
