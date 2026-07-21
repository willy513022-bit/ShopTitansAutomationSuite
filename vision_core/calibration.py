from __future__ import annotations

from dataclasses import dataclass

import cv2

from vision.capture import screenshot
from vision_core.frame import Frame
from vision_core.roi import ROI
from vision_core.roi_store import ROIStore


@dataclass(frozen=True)
class CalibrationResult:
    roi: ROI
    saved: bool


class ROICalibrator:
    def __init__(
        self,
        store: ROIStore | None = None,
    ) -> None:
        self.store = store or ROIStore()

    def calibrate(
        self,
        name: str,
    ) -> CalibrationResult:
        image = screenshot()

        if image is None:
            raise RuntimeError(
                "無法擷取 Shop Titans 視窗"
            )

        frame = Frame.from_image(image)

        x, y, width, height = cv2.selectROI(
            f"Select ROI: {name}",
            frame.image,
            showCrosshair=True,
            fromCenter=False,
        )

        cv2.destroyAllWindows()

        roi = ROI(
            name=name,
            x=int(x),
            y=int(y),
            width=int(width),
            height=int(height),
        )

        if width <= 0 or height <= 0:
            return CalibrationResult(
                roi=roi,
                saved=False,
            )

        self.store.save(roi)

        return CalibrationResult(
            roi=roi,
            saved=True,
        )
