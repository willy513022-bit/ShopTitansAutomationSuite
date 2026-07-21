from __future__ import annotations

import cv2
import numpy as np


def upscale(
    image: np.ndarray,
    scale: float = 3.0,
) -> np.ndarray:
    if image is None or image.size == 0:
        return image

    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )


def grayscale(
    image: np.ndarray,
) -> np.ndarray:
    if image is None or image.size == 0:
        return image

    if len(image.shape) == 2:
        return image

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )


def high_contrast_digits(
    image: np.ndarray,
) -> np.ndarray:
    if image is None or image.size == 0:
        return image

    image = upscale(image, 4.0)
    gray = grayscale(image)
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0,
    )

    return cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY
        + cv2.THRESH_OTSU,
    )[1]
