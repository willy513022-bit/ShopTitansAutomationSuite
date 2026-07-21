from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DEBUG_ROOT = (
    PROJECT_ROOT
    / "data"
    / "screenshots"
    / "vision_debug"
)


def save_debug_image(
    filename: str,
    image: np.ndarray,
) -> Path:
    DEBUG_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = DEBUG_ROOT / filename

    if image is None or image.size == 0:
        raise ValueError(
            "無法儲存空白影像"
        )

    if not cv2.imwrite(
        str(path),
        image,
    ):
        raise OSError(
            f"影像儲存失敗：{path}"
        )

    return path
