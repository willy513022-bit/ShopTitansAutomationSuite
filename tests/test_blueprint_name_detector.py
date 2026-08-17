import numpy as np
import pytest

from services.blueprint_name_matcher import (
    BlueprintNameMatcher,
)
from vision.blueprint_name_detector import (
    BlueprintNameDetector,
)
from vision.blueprint_name_models import (
    BlueprintNameOCRResult,
)
from vision.blueprint_progress_models import (
    ImageRegion,
)


class FakeOCR:
    def __init__(
        self,
        text: str,
        confidence: float,
    ):
        self.text = text
        self.confidence = confidence
        self.received_image = None

    def read(
        self,
        image,
    ):
        self.received_image = image

        return BlueprintNameOCRResult(
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


def make_card():
    return ImageRegion(
        x=100,
        y=100,
        width=207,
        height=250,
    )


def test_detector_returns_raw_name_without_matcher():
    detector = BlueprintNameDetector(
        ocr_reader=FakeOCR(
            "Bleakspire Roots",
            0.95,
        )
    )

    result = detector.detect(
        make_image(),
        make_card(),
    )

    assert (
        result.item_name
        == "Bleakspire Roots"
    )

    assert result.detected


def test_detector_uses_matcher():
    matcher = BlueprintNameMatcher(
        [
            "Bleakspire Roots",
            "Lost Star Chart",
        ]
    )

    detector = BlueprintNameDetector(
        ocr_reader=FakeOCR(
            "Bleakspire Root5",
            0.95,
        ),
        matcher=matcher,
    )

    result = detector.detect(
        make_image(),
        make_card(),
    )

    assert (
        result.item_name
        == "Bleakspire Roots"
    )

    assert result.match_score is not None


def test_low_ocr_confidence_is_rejected():
    detector = BlueprintNameDetector(
        ocr_reader=FakeOCR(
            "Bleakspire Roots",
            0.20,
        ),
        minimum_ocr_confidence=0.80,
    )

    result = detector.detect(
        make_image(),
        make_card(),
    )

    assert result.item_name is None
    assert not result.detected


def test_detector_sends_upscaled_image_to_ocr():
    fake = FakeOCR(
        "Test",
        1.0,
    )

    detector = BlueprintNameDetector(
        ocr_reader=fake,
        upscale=4.0,
    )

    result = detector.detect(
        make_image(),
        make_card(),
    )

    assert result.name_region.width > 0
    assert result.name_region.height > 0

    assert fake.received_image is not None

    assert (
        fake.received_image.shape[1]
        == result.name_region.width * 4
    )

    assert (
        fake.received_image.shape[0]
        == result.name_region.height * 4
    )


def test_empty_image_rejected():
    detector = BlueprintNameDetector(
        ocr_reader=FakeOCR(
            "",
            0.0,
        )
    )

    with pytest.raises(ValueError):
        detector.detect(
            np.empty(
                (0, 0),
                dtype=np.uint8,
            ),
            make_card(),
        )


def test_non_array_image_rejected():
    detector = BlueprintNameDetector(
        ocr_reader=FakeOCR(
            "",
            0.0,
        )
    )

    with pytest.raises(TypeError):
        detector.detect(
            "not image",
            make_card(),
        )


def test_invalid_card_region_rejected():
    detector = BlueprintNameDetector(
        ocr_reader=FakeOCR(
            "",
            0.0,
        )
    )

    with pytest.raises(TypeError):
        detector.detect(
            make_image(),
            object(),
        )


def test_invalid_confidence_threshold():
    with pytest.raises(ValueError):
        BlueprintNameDetector(
            minimum_ocr_confidence=1.1,
        )


def test_invalid_upscale():
    with pytest.raises(ValueError):
        BlueprintNameDetector(
            upscale=0,
        )