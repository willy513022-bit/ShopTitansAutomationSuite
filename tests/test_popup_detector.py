from pathlib import Path

import cv2
import numpy as np
import pytest

from vision.popup_detector import PopupDetector, PopupTemplate
from vision.popup_models import PopupType
from vision.template_matcher import TemplateMatcher


class StubResult:
    def __init__(self, confidence: float, location=(4, 6), size=(10, 8)):
        self.confidence = confidence
        self.location = location if confidence >= 0.8 else None
        self.size = size if confidence >= 0.8 else None

    @property
    def matched(self):
        return self.location is not None


class StubMatcher:
    def __init__(self, scores):
        self.scores = scores

    def match(self, screenshot, template, template_name="template"):
        return StubResult(self.scores.get(template_name, 0.0))


def image(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 255, size=(12, 14, 3), dtype=np.uint8)


def test_detector_selects_best_variant_per_popup_type():
    matcher = StubMatcher(
        {
            "popup:reconnect:error_1000": 0.91,
            "popup:reconnect:error_4006": 0.97,
            "popup:paid_offer:naya": 0.93,
        }
    )
    detector = PopupDetector(matcher=matcher)
    detector.register(
        PopupType.RECONNECT,
        PopupTemplate("error_1000", image(1)),
    )
    detector.register(
        PopupType.RECONNECT,
        PopupTemplate("error_4006", image(2)),
    )
    detector.register(
        PopupType.PAID_OFFER,
        PopupTemplate("naya", image(3)),
    )

    detections = detector.detect(image(9))
    assert len(detections) == 2
    reconnect = next(x for x in detections if x.popup_type is PopupType.RECONNECT)
    assert reconnect.template_id == "error_4006"
    assert reconnect.confidence == 0.97


def test_detector_returns_none_when_nothing_matches():
    detector = PopupDetector(matcher=StubMatcher({}))
    detector.register(
        PopupType.UPGRADE_FINISHED,
        PopupTemplate("complete", image(4)),
    )
    assert detector.detect_best(image(5)) is None


def test_duplicate_template_id_is_rejected():
    detector = PopupDetector()
    template = PopupTemplate("same", image(1))
    detector.register(PopupType.RECONNECT, template)
    with pytest.raises(ValueError):
        detector.register(PopupType.RECONNECT, template)


def test_register_file_and_exact_asset_match(tmp_path):
    template = image(7)
    path = tmp_path / "popup.png"
    assert cv2.imwrite(str(path), template)

    detector = PopupDetector(matcher=TemplateMatcher(threshold=0.99))
    detector.register_file(PopupType.RECONNECT, path, "file_variant")
    detection = detector.detect_best(template)

    assert detection is not None
    assert detection.popup_type is PopupType.RECONNECT
    assert detection.template_id == "file_variant"
    assert detection.confidence >= 0.99


def test_invalid_popup_type_is_rejected():
    detector = PopupDetector()
    with pytest.raises(ValueError):
        detector.register("not_a_popup", PopupTemplate("x", image(1)))
