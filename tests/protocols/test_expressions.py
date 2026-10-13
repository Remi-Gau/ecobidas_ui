import json
from decimal import Decimal
from pathlib import Path

import pytest

from ecobidas_ui.protocols.expressions import (
    UnsupportedExpression,
    evaluate,
    is_true,
    to_value,
)
from ecobidas_ui.protocols.utils import local_cobidas_schema


@pytest.mark.parametrize(
    "expression, values, expected",
    [
        # the kinds of expressions found in the schemas
        ("01", {}, True),
        ("if_design_includes_blocks", {"if_design_includes_blocks": 1}, True),
        ("if_design_includes_blocks", {}, False),
        ("analysis_type == 0", {"analysis_type": 0}, True),
        ("analysis_type == 0", {"analysis_type": 1}, False),
        ("contrast_agent_used==1", {"contrast_agent_used": 1}, True),
        ("volume_censoring_used  == 1", {"volume_censoring_used": 1}, True),
        ("number_response_classes > 2", {"number_response_classes": 3}, True),
        ("number_response_classes > 2", {"number_response_classes": None}, False),
        ("type_of_design in  [0, 2]", {"type_of_design": 2}, True),
        ("type_of_design in  [0, 2]", {"type_of_design": 1}, False),
        ("modality.includes(4)", {"modality": [1, 4]}, True),
        ("modality.includes(4)", {"modality": [1]}, False),
        ("modality.includes(4)", {"modality": None}, False),
        ("[1, 2].includes(perf_labelling_method)", {"perf_labelling_method": 2}, True),
        ("[1, 2].includes(perf_labelling_method)", {"perf_labelling_method": 0}, False),
        ("a == 0 && b.includes(5)", {"a": 0, "b": [5]}, True),
        ("a == 0 && b.includes(5)", {"a": 1, "b": [5]}, False),
        ("a == 1 || b ==1", {"a": 0, "b": 1}, True),
        ("a == 1 and b == 1", {"a": 1, "b": 0}, False),
        (
            "subject_age_min > subject_age_mean",
            {"subject_age_min": 30, "subject_age_mean": 25},
            True,
        ),
        ("subject_age_min > subject_age_mean", {}, False),
        # other javascript syntax
        ("!a", {"a": 0}, True),
        ("a != 1", {"a": 0}, True),
        ("a === 1", {"a": 1}, True),
        ("a !== 1", {"a": 1}, False),
        ("a == null", {}, True),
        ("a == true", {"a": True}, True),
        ("a > -1", {"a": 0}, True),
        ("a == 'text'", {"a": "text"}, True),
    ],
)
def test_evaluate(expression, values, expected):
    assert evaluate(expression, values) is expected


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('ls')",
        "open('secret.txt')",
        "a.__class__",
        "(lambda: 1)()",
        "[x for x in a]",
        "a + 1",
        "a[0]",
        "a.append(1)",
        "a.includes(1, 2)",
        "a is None",
    ],
)
def test_evaluate_unsafe_expressions(expression):
    with pytest.raises(UnsupportedExpression):
        evaluate(expression, {"a": [1]})
    assert is_true(expression, {"a": [1]}) is False


def test_evaluate_invalid_expression():
    with pytest.raises(SyntaxError):
        evaluate("partial fourrier used == 1", {})
    assert is_true("partial fourrier used == 1", {}) is False


def test_answers_are_not_executed(tmp_path):
    target = tmp_path / "pwned"
    answer = f"__import__('pathlib').Path('{target}').touch()"

    assert is_true("a == 1", {"a": to_value(answer)}) is False
    assert not target.exists()


@pytest.mark.parametrize(
    "answer, expected",
    [
        (None, None),
        ("", None),
        ("  ", None),
        ("1", 1),
        (" 2 ", 2),
        ("2.5", 2.5),
        ("text", "text"),
        (0, 0),
        (Decimal("3"), 3),
        (Decimal("3.5"), 3.5),
        (["1", "2"], [1, 2]),
    ],
)
def test_to_value(answer, expected):
    assert to_value(answer) == expected


# expressions that are not valid in the schemas
KNOWN_INVALID_EXPRESSIONS = {"partial fourrier used == 1"}


def schema_expressions():
    expressions = set()
    for file in (local_cobidas_schema() / "schemas").rglob("*"):
        if not file.is_file():
            continue
        try:
            content = json.loads(Path(file).read_text())
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(content, dict):
            continue
        for item in content.get("ui", {}).get("addProperties", []) or []:
            if isinstance(item.get("isVis"), str):
                expressions.add(item["isVis"])
        for message in content.get("messages", []) or []:
            expressions.add(message["jsExpression"])
    return sorted(expressions - KNOWN_INVALID_EXPRESSIONS)


@pytest.mark.parametrize("expression", schema_expressions())
def test_schema_expressions_are_supported(expression):
    evaluate(expression, {})
