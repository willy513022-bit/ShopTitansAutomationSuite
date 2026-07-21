from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Frame:
    image: np.ndarray
    width: int
    height: int

    @classmethod
    def from_image(
        cls,
        image: np.ndarray,
    ) -> "Frame":
        height, width = image.shape[:2]
        return cls(
            image=image,
            width=width,
            height=height,
        )
