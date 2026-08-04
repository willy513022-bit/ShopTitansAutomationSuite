import numpy as np
import pytest

from vision.blueprint_progress_detector import (
    BlueprintProgressDetector,
)
from vision.blueprint_progress_models import (
    BlueprintProgressOCRResult,
    ImageRegion,
)
from vision.blueprint_progress_regions import (
    BlueprintProgressRegionConfig,
    BlueprintProgressRegionLocator,
)


class FakeOCR:
    def __init__(
        self,
        text: str,
        confidence: float = 0.95,
    ) -> None:
        self.text = text
        self.confidence = confidence
        self.received_image = None

    def read(
        self,
        image: np.ndarray,
    ) -> BlueprintProgressOCRResult:
        self.received_image = image

        return BlueprintProgressOCRResult(
            text=self.text,
            confidence=self.confidence,
        )


def make_image() -> np.ndarray:
    return np.zeros(
        (600, 800, 3),
        dtype=np.uint8,
    )


def test_detector_parses_progress():
    ocr = FakeOCR("10/15")

    detector = BlueprintProgressDetector(
        ocr_reader=ocr,
    )

    result = detector.detect(
        image=make_image(),
        card_region=ImageRegion(
            x=100,
            y=100,
            width=300,
            height=400,
        ),
    )

    assert result.detected
    assert result.current_progress == 10
    assert result.current_target == 15
    assert result.remaining == 5
    assert not result.complete


def test_detector_handles_ocr_misread():
    detector = BlueprintProgressDetector(
        ocr_reader=FakeOCR(
            "Progress 1O / I5"
        ),
    )

    result = detector.detect(
        image=make_image(),
        card_region=ImageRegion(
            x=100,
            y=100,
            width=300,
            height=400,
        ),
    )

    assert result.detected
    assert result.current_progress == 10
    assert result.current_target == 15


def test_invalid_ocr_text_returns_detection_without_parse():
    detector = BlueprintProgressDetector(
        ocr_reader=FakeOCR("unknown"),
    )

    result = detector.detect(
        image=make_image(),
        card_region=ImageRegion(
            x=100,
            y=100,
            width=300,
            height=400,
        ),
    )

    assert not result.detected
    assert result.parsed is None
    assert result.ocr_text == "unknown"


def test_low_confidence_is_not_parsed():
    detector = BlueprintProgressDetector(
        ocr_reader=FakeOCR(
            "10/15",
            confidence=0.40,
        ),
        minimum_confidence=0.80,
    )

    result = detector.detect(
        image=make_image(),
        card_region=ImageRegion(
            x=100,
            y=100,
            width=300,
            height=400,
        ),
    )

    assert not result.detected
    assert result.ocr_text == "10/15"
    assert result.ocr_confidence == 0.40


def test_completed_progress():
    detector = BlueprintProgressDetector(
        ocr_reader=FakeOCR("15/15"),
    )

    result = detector.detect(
        image=make_image(),
        card_region=ImageRegion(
            x=100,
            y=100,
            width=300,
            height=400,
        ),
    )

    assert result.complete
    assert result.remaining == 0


def test_detector_sends_prepared_image_to_ocr():
    ocr = FakeOCR("0/7")

    config = BlueprintProgressRegionConfig(
        x_fraction=0.0,
        y_fraction=0.0,
        width_fraction=0.5,
        height_fraction=0.5,
    )

    detector = BlueprintProgressDetector(
        region_locator=(
            BlueprintProgressRegionLocator(
                config
            )
        ),
        ocr_reader=ocr,
        upscale=2.0,
    )

    detector.detect(
        image=make_image(),
        card_region=ImageRegion(
            x=0,
            y=0,
            width=200,
            height=100,
        ),
    )

    assert ocr.received_image is not None

    # 原始裁切是 100 × 50，
    # upscale=2 後應成為 200 × 100。
    assert ocr.received_image.shape == (
        100,
        200,
    )


def test_empty_image_rejected():
    detector = BlueprintProgressDetector(
        ocr_reader=FakeOCR("10/15"),
    )

    with pytest.raises(ValueError):
        detector.detect(
            image=np.empty(
                (0, 0, 3),
                dtype=np.uint8,
            ),
            card_region=ImageRegion(
                x=0,
                y=0,
                width=10,
                height=10,
            ),
        )


def test_non_array_image_rejected():
    detector = BlueprintProgressDetector(
        ocr_reader=FakeOCR("10/15"),
    )

    with pytest.raises(TypeError):
        detector.detect(
            image=object(),
            card_region=ImageRegion(
                x=0,
                y=0,
                width=10,
                height=10,
            ),
        )


def test_invalid_confidence_threshold_rejected():
    with pytest.raises(ValueError):
        BlueprintProgressDetector(
            ocr_reader=FakeOCR("10/15"),
            minimum_confidence=1.1,
        )