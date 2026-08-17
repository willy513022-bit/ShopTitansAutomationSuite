import numpy as np
import pytest

from services.blueprint_name_matcher import (
    BlueprintNameMatcher,
)
from vision.blueprint_card_locator import (
    BlueprintCard,
)
from vision.blueprint_card_scanner import (
    BlueprintCardScanner,
    BlueprintCardState,
)
from vision.blueprint_name_detector import (
    BlueprintNameDetector,
)
from vision.blueprint_name_models import (
    BlueprintNameOCRResult,
)
from vision.blueprint_progress_detector import (
    BlueprintProgressDetector,
)
from vision.blueprint_progress_models import (
    BlueprintProgressOCRResult,
    ImageRegion,
)


class FakeNameOCR:
    def __init__(
        self,
        text: str,
        confidence: float = 0.95,
    ):
        self.text = text
        self.confidence = confidence

    def read(
        self,
        image,
    ):
        return BlueprintNameOCRResult(
            text=self.text,
            confidence=self.confidence,
        )


class FakeProgressOCR:
    def __init__(
        self,
        text: str,
        confidence: float = 0.95,
    ):
        self.text = text
        self.confidence = confidence

    def read(
        self,
        image,
    ):
        return BlueprintProgressOCRResult(
            text=self.text,
            confidence=self.confidence,
        )


def make_image():
    return np.zeros(
        (
            1000,
            1000,
            3,
        ),
        dtype=np.uint8,
    )


def make_card(
    *,
    row=0,
    column=0,
):
    return BlueprintCard(
        row=row,
        column=column,
        region=ImageRegion(
            x=100 + column * 220,
            y=100 + row * 260,
            width=207,
            height=250,
        ),
    )


def make_scanner(
    *,
    name_text="Opulent Decoction",
    progress_text="4/6",
):
    matcher = BlueprintNameMatcher(
        [
            "Opulent Decoction",
            "Bleakspire Roots",
        ]
    )

    name_detector = (
        BlueprintNameDetector(
            ocr_reader=FakeNameOCR(
                name_text
            ),
            matcher=matcher,
        )
    )

    progress_detector = (
        BlueprintProgressDetector(
            ocr_reader=FakeProgressOCR(
                progress_text
            )
        )
    )

    return BlueprintCardScanner(
        name_detector=name_detector,
        progress_detector=(
            progress_detector
        ),
    )


def test_scan_card_returns_state():
    scanner = make_scanner()

    state = scanner.scan_card(
        image=make_image(),
        card=make_card(),
    )

    assert isinstance(
        state,
        BlueprintCardState,
    )

    assert (
        state.item_name
        == "Opulent Decoction"
    )

    assert state.current_progress == 4
    assert state.current_target == 6
    assert state.remaining == 2

    assert state.valid


def test_state_progress_text():
    state = make_scanner().scan_card(
        image=make_image(),
        card=make_card(),
    )

    assert state.progress_text == "4/6"


def test_state_milestone_complete():
    scanner = make_scanner(
        progress_text="6/6"
    )

    state = scanner.scan_card(
        image=make_image(),
        card=make_card(),
    )

    assert state.remaining == 0
    assert state.milestone_complete


def test_invalid_progress_produces_partial_state():
    scanner = make_scanner(
        progress_text="unknown"
    )

    state = scanner.scan_card(
        image=make_image(),
        card=make_card(),
    )

    assert state.has_name
    assert not state.has_progress
    assert not state.valid

    assert (
        state.current_progress
        is None
    )

    assert state.progress_text == "?/?"


def test_invalid_name_produces_partial_state():
    matcher = BlueprintNameMatcher(
        [
            "Opulent Decoction",
        ],
        minimum_score=0.90,
    )

    scanner = BlueprintCardScanner(
        name_detector=(
            BlueprintNameDetector(
                ocr_reader=FakeNameOCR(
                    "totally unknown",
                    0.95,
                ),
                matcher=matcher,
            )
        ),
        progress_detector=(
            BlueprintProgressDetector(
                ocr_reader=FakeProgressOCR(
                    "4/6"
                )
            )
        ),
    )

    state = scanner.scan_card(
        image=make_image(),
        card=make_card(),
    )

    assert not state.has_name
    assert state.has_progress
    assert not state.valid


def test_scan_multiple_cards():
    scanner = make_scanner()

    cards = [
        make_card(
            row=0,
            column=0,
        ),
        make_card(
            row=0,
            column=1,
        ),
        make_card(
            row=1,
            column=0,
        ),
    ]

    states = scanner.scan(
        image=make_image(),
        cards=cards,
    )

    assert len(states) == 3

    assert [
        (
            state.row,
            state.column,
        )
        for state in states
    ] == [
        (0, 0),
        (0, 1),
        (1, 0),
    ]


def test_scan_returns_tuple():
    scanner = make_scanner()

    states = scanner.scan(
        image=make_image(),
        cards=[
            make_card(),
        ],
    )

    assert isinstance(
        states,
        tuple,
    )


def test_state_confidence_is_preserved():
    matcher = BlueprintNameMatcher(
        [
            "Bleakspire Roots",
        ]
    )

    scanner = BlueprintCardScanner(
        name_detector=(
            BlueprintNameDetector(
                ocr_reader=FakeNameOCR(
                    "Bleakspire Roots",
                    0.91,
                ),
                matcher=matcher,
            )
        ),
        progress_detector=(
            BlueprintProgressDetector(
                ocr_reader=FakeProgressOCR(
                    "4/6",
                    0.88,
                )
            )
        ),
    )

    state = scanner.scan_card(
        image=make_image(),
        card=make_card(),
    )

    assert (
        state.name_confidence
        == pytest.approx(0.91)
    )

    assert (
        state.progress_confidence
        == pytest.approx(0.88)
    )


def test_state_rejects_inconsistent_remaining():
    with pytest.raises(ValueError):
        BlueprintCardState(
            row=0,
            column=0,
            card_region=ImageRegion(
                x=0,
                y=0,
                width=100,
                height=100,
            ),
            item_name="Example",
            current_progress=4,
            current_target=6,
            remaining=99,
            name_confidence=1.0,
            progress_confidence=1.0,
        )


def test_state_rejects_partial_progress_values():
    with pytest.raises(ValueError):
        BlueprintCardState(
            row=0,
            column=0,
            card_region=ImageRegion(
                x=0,
                y=0,
                width=100,
                height=100,
            ),
            item_name="Example",
            current_progress=4,
            current_target=None,
            remaining=None,
            name_confidence=1.0,
            progress_confidence=1.0,
        )


def test_empty_image_rejected():
    scanner = make_scanner()

    with pytest.raises(ValueError):
        scanner.scan(
            image=np.empty(
                (0, 0),
                dtype=np.uint8,
            ),
            cards=[],
        )


def test_non_array_image_rejected():
    scanner = make_scanner()

    with pytest.raises(TypeError):
        scanner.scan(
            image="invalid",
            cards=[],
        )


def test_invalid_card_rejected():
    scanner = make_scanner()

    with pytest.raises(TypeError):
        scanner.scan_card(
            image=make_image(),
            card=object(),
        )