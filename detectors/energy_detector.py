from __future__ import annotations

from dataclasses import dataclass

from recognizers.energy_recognizer import (
    EnergyRecognitionResult,
    EnergyRecognizer,
)
from vision.capture import screenshot
from vision_core.debug_writer import (
    save_debug_image,
)
from vision_core.frame import Frame
from vision_core.roi_store import ROIStore


@dataclass(frozen=True)
class EnergyDetectionResult:
    recognized: EnergyRecognitionResult
    debug_image_path: str | None

    @property
    def valid(self) -> bool:
        return self.recognized.valid


class EnergyDetector:
    ROI_NAME = "energy_value"

    def __init__(
        self,
        store: ROIStore | None = None,
        recognizer: EnergyRecognizer | None = None,
    ) -> None:
        self.store = store or ROIStore()
        self.recognizer = (
            recognizer
            or EnergyRecognizer()
        )

    def detect(
        self,
        save_debug: bool = True,
    ) -> EnergyDetectionResult:
        image = screenshot()

        if image is None:
            raise RuntimeError(
                "無法擷取 Shop Titans 視窗"
            )

        frame = Frame.from_image(image)

        roi = self.store.get(
            self.ROI_NAME
        )

        if roi is None:
            raise RuntimeError(
                "尚未校準 energy_value ROI；"
                "請先執行 "
                "py -m tests.calibrate_energy_roi"
            )

        if not roi.validate(frame):
            raise RuntimeError(
                "energy_value ROI 超出目前畫面範圍；"
                "請重新校準"
            )

        crop = roi.crop(frame)

        debug_path = None

        if save_debug:
            debug_path = str(
                save_debug_image(
                    "energy_roi.png",
                    crop,
                )
            )

        recognized = (
            self.recognizer
            .recognize(crop)
        )

        return EnergyDetectionResult(
            recognized=recognized,
            debug_image_path=debug_path,
        )
