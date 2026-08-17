import pytest

from services.blueprint_name_matcher import (
    BlueprintNameMatcher,
)


ITEM_NAMES = [
    "Angler's Veil",
    "Lost Star Chart",
    "Opulent Incantation",
    "Opulent Decoction",
    "Ice Queen's Summer Hat",
    "Bleakspire Roots",
]


def make_matcher():
    return BlueprintNameMatcher(
        ITEM_NAMES,
        minimum_score=0.70,
    )


def test_exact_match():
    result = make_matcher().match(
        "Opulent Decoction"
    )

    assert result is not None
    assert (
        result.item_name
        == "Opulent Decoction"
    )

    assert result.score == 1.0


def test_apostrophe_can_be_missing():
    result = make_matcher().match(
        "Anglers Veil"
    )

    assert result is not None
    assert (
        result.item_name
        == "Angler's Veil"
    )


def test_queens_apostrophe_can_be_missing():
    result = make_matcher().match(
        "Ice Queens Summer Hat"
    )

    assert result is not None
    assert (
        result.item_name
        == "Ice Queen's Summer Hat"
    )


def test_small_ocr_error_can_be_corrected():
    result = make_matcher().match(
        "Bleakspire Root5"
    )

    assert result is not None
    assert (
        result.item_name
        == "Bleakspire Roots"
    )


def test_similar_opulent_names_are_separated():
    matcher = make_matcher()

    incantation = matcher.match(
        "Opulent Incantation"
    )

    decoction = matcher.match(
        "Opulent Decoction"
    )

    assert incantation is not None
    assert decoction is not None

    assert (
        incantation.item_name
        == "Opulent Incantation"
    )

    assert (
        decoction.item_name
        == "Opulent Decoction"
    )


def test_empty_returns_none():
    assert (
        make_matcher().match("")
        is None
    )


def test_low_similarity_returns_none():
    matcher = BlueprintNameMatcher(
        ITEM_NAMES,
        minimum_score=0.90,
    )

    assert (
        matcher.match(
            "completely unrelated"
        )
        is None
    )


def test_duplicates_are_removed():
    matcher = BlueprintNameMatcher(
        [
            "Bleakspire Roots",
            "Bleakspire Roots",
        ]
    )

    assert matcher.item_names == (
        "Bleakspire Roots",
    )


def test_invalid_minimum_score():
    with pytest.raises(ValueError):
        BlueprintNameMatcher(
            ITEM_NAMES,
            minimum_score=1.1,
        )


def test_normalize():
    assert (
        BlueprintNameMatcher.normalize(
            "  Ice Queen’s   Summer Hat  "
        )
        == "ice queens summer hat"
    )