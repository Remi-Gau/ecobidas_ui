"""Safely evaluate the conditions defined in the schemas.

The visibility conditions (``isVis``) and the validation messages (``jsExpression``)
of the schemas are written in javascript, for example
``single_preprocessing_software == 0 && operation_performed.includes(5)``.

They are translated to python syntax, parsed, and evaluated by walking their syntax tree.
Only literals, item names, comparisons, boolean operators and ``includes`` are allowed:
the answers of the form are looked up as values and are never executed.
"""

import ast
import logging
import operator
import re
from collections.abc import Callable
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)


class UnsupportedExpression(ValueError):
    """The expression uses syntax that is not allowed."""


# item names can contain hyphens (for example "fitting-description"):
# they are replaced so that they are not parsed as subtractions
HYPHEN = "_hyphen_"
HYPHENATED_NAME = r"\b[A-Za-z_]\w*(?:-[A-Za-z_]\w*)+\b"

# applied in order
JS_TO_PYTHON = [
    (r"!==?", "!="),
    (r"===?", "=="),
    # "!" but not "!="
    (r"!(?!=)", " not "),
    (r"&&", " and "),
    (r"\|\|", " or "),
    (r"\btrue\b", "True"),
    (r"\bfalse\b", "False"),
    (r"\b(null|undefined)\b", "None"),
    # leading zeros are not valid in python: 01 -> 1
    (r"\b0+(?=\d)", ""),
]

COMPARISONS: dict[type[ast.cmpop], Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda item, container: item in container,
    ast.NotIn: lambda item, container: item not in container,
}


def to_python(expression: str) -> str:
    """Translate a javascript expression to python syntax.

    >>> to_python("a == 0 && b.includes(5) || !c")
    'a == 0  and  b.includes(5)  or   not c'
    """
    expression = re.sub(HYPHENATED_NAME, lambda match: _name(match.group()), expression)
    for pattern, replacement in JS_TO_PYTHON:
        expression = re.sub(pattern, replacement, expression)
    return expression.strip()


def _name(item_name: str) -> str:
    """Return the python name used for an item in the expressions."""
    return item_name.replace("-", HYPHEN)


def evaluate(expression: str, values: dict[str, Any]) -> bool:
    """Evaluate an expression with the given values of the items.

    Items without a value are ``None``.
    Comparisons between values of incompatible types are false.

    Raises
    ------
    SyntaxError
        If the expression cannot be parsed.
    UnsupportedExpression
        If the expression uses syntax that is not allowed.

    >>> evaluate("a == 0 && b.includes(5)", {"a": 0, "b": [1, 5]})
    True
    >>> evaluate("a > 2", {"a": None})
    False
    >>> evaluate("fitting-description == 1", {"fitting-description": 1})
    True
    """
    tree = ast.parse(to_python(expression), mode="eval")
    return bool(_evaluate(tree.body, {_name(key): value for key, value in values.items()}))


def is_true(expression: str, values: dict[str, Any]) -> bool:
    """Evaluate an expression, considering invalid expressions as false."""
    try:
        return evaluate(expression, values)
    except (SyntaxError, UnsupportedExpression) as exc:
        logger.error(f"Could not evaluate the expression '{expression}': {exc}")
        return False


# one return per allowed type of node
def _evaluate(node: ast.AST, values: dict[str, Any]) -> Any:  # noqa: PLR0911
    match node:
        case ast.Constant(value=value) if value is None or isinstance(
            value, bool | int | float | str
        ):
            return value

        case ast.Name(id=name):
            return values.get(name)

        case ast.List(elts=elements) | ast.Tuple(elts=elements):
            return [_evaluate(element, values) for element in elements]

        case ast.UnaryOp(op=ast.Not(), operand=operand):
            return not _evaluate(operand, values)

        case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=int() | float() as value)):
            return -value

        case ast.BoolOp(op=ast.And(), values=operands):
            return all(_evaluate(operand, values) for operand in operands)

        case ast.BoolOp(op=ast.Or(), values=operands):
            return any(_evaluate(operand, values) for operand in operands)

        case ast.Compare(left=left, ops=ops, comparators=comparators):
            left_value = _evaluate(left, values)
            for op, comparator in zip(ops, comparators, strict=True):
                right_value = _evaluate(comparator, values)
                if not _compare(op, left_value, right_value):
                    return False
                left_value = right_value
            return True

        # javascript: container.includes(item)
        case ast.Call(
            func=ast.Attribute(value=container, attr="includes"), args=[item], keywords=[]
        ):
            return _compare(ast.In(), _evaluate(item, values), _evaluate(container, values))

    raise UnsupportedExpression(f"'{ast.unparse(node)}' is not allowed")


def _compare(op: ast.cmpop, left: Any, right: Any) -> bool:
    if type(op) not in COMPARISONS:
        raise UnsupportedExpression(f"'{type(op).__name__}' comparisons are not allowed")
    try:
        return COMPARISONS[type(op)](left, right)
    except TypeError:
        # for example: None > 2, or 5 in None
        return False


def to_value(answer: Any) -> Any:
    """Convert an answer of the form to a value usable in expressions.

    Empty answers are None, and numbers submitted as text are converted to numbers.

    >>> to_value(["1", "2.5", "", "a"])
    [1, 2.5, None, 'a']
    """
    if isinstance(answer, list | tuple):
        return [to_value(element) for element in answer]
    if isinstance(answer, Decimal):
        return int(answer) if answer == answer.to_integral_value() else float(answer)
    if isinstance(answer, str):
        answer = answer.strip()
        if not answer:
            return None
        for number_type in (int, float):
            try:
                return number_type(answer)
            except ValueError:
                pass
    return answer
