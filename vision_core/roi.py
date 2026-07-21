from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from vision_core.frame import Frame


@dataclass(frozen=True)
class ROI:
    name: str
    x: int
    y: int
    width: int
    height: int

    def crop(
        self,
        frame: Frame,
    ) -> np.ndarray:
        left = max(0, self.x)
        top = max(0, self.y)
        right = min(
            frame.width,
            self.x + self.width,
        )
        bottom = min(
            frame.height,
            self.y + self.height,
        )

        if right <= left or bottom <= top:
            return frame.image[0:0, 0:0].copy()

        return frame.image[
            top:bottom,
            left:right,
        ].copy()

    def validate(
        self,
        frame: Frame,
    ) -> bool:
        return (
            self.width > 0
            and self.height > 0
            and self.x < frame.width
            and self.y < frame.height
            and self.x + self.width > 0
            and self.y + self.height > 0
        )
