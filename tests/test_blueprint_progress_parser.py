import pytest

from services.blueprint_progress_parser import (
    BlueprintProgressParser,
    ParsedBlueprintProgress,
)


@pytest.fixture
def parser() -> BlueprintProgressParser:
    return BlueprintProgressParser()


@pytest.mark.parametrize(
    ("text", "current", "target"),
    [
        ("10/15", 10, 15),
        ("0/7", 0, 7),
        ("14 / 15", 14, 15),
        ("10／15", 10, 15),
        ("1O/15", 10, 15),
        ("O/7", 0, 7),
        ("I0/I5", 10, 15),
        ("l0/l5", 10, 15),
        ("10\\15", 10, 15),
        ("Progress 10/15", 10, 15),
        ("里程碑 10 / 15", 10, 15),
        ("10/15 items", 10, 15),
        ("  10 / 15  ", 10, 15),
        ("10\n/\n15", 10, 15),
    ],
)
def test_parse_supported_formats(
    parser: BlueprintProgressParser,
    text: str,
    current: int,
    target: int,
) -> None:
    result = parser.parse(text)

    assert result is not None
    assert result.current_progress == current
    assert result.current_target == target
    assert result.remaining == target - current


def test_completed_progress(
    parser: BlueprintProgressParser,
) -> None:
    result = parser.parse("15/15")

    assert result is not None
    assert result.complete
    assert result.remaining == 0


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "abc",
        "/",
        "/15",
        "10/",
        "10-15",
        "10:15",
        "20/15",
        "0/0",
        "Progress unavailable",
    ],
)
def test_invalid_text_returns_none(
    parser: BlueprintProgressParser,
    text: str,
) -> None:
    assert parser.parse(text) is None


def test_multiple_progress_values_are_rejected(
    parser: BlueprintProgressParser,
) -> None:
    text = "First 3/7 Second 10/15"

    assert parser.parse(text) is None


def test_parse_required_returns_result(
    parser: BlueprintProgressParser,
) -> None:
    result = parser.parse_required("10/15")

    assert isinstance(
        result,
        ParsedBlueprintProgress,
    )
    assert result.current_progress == 10
    assert result.current_target == 15


def test_parse_required_raises_for_invalid_text(
    parser: BlueprintProgressParser,
) -> None:
    with pytest.raises(ValueError):
        parser.parse_required("invalid")


def test_parse_rejects_non_string(
    parser: BlueprintProgressParser,
) -> None:
    with pytest.raises(TypeError):
        parser.parse(123)  # type: ignore[arg-type]


def test_normalize_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        BlueprintProgressParser.normalize(
            None  # type: ignore[arg-type]
        )


def test_normalized_text_is_preserved(
    parser: BlueprintProgressParser,
) -> None:
    result = parser.parse("  Progress\n1O ／ I5  ")

    assert result is not None
    assert result.normalized_text == (
        "Progress 10 / 15"
    )
    assert result.raw_text == (
        "  Progress\n1O ／ I5  "
    )