from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

import numpy as np
from rapidocr_onnxruntime import RapidOCR


@dataclass(frozen=True)
class OCRLine:
    text: str
    confidence: float


class SharedOCREngine:
    _instance: "SharedOCREngine | None" = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(
                    cls
                )
                cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        print("正在載入共用 RapidOCR...")
        self._engine = RapidOCR()
        self._initialized = True
        print("共用 RapidOCR 載入完成")

    def read(
        self,
        image: np.ndarray,
    ) -> list[OCRLine]:
        if image is None or image.size == 0:
            return []

        result, _elapsed = self._engine(image)

        if not result:
            return []

        lines: list[OCRLine] = []

        for item in result:
            if len(item) < 3:
                continue

            text = str(item[1]).strip()

            if not text:
                continue

            try:
                confidence = float(item[2])
            except (TypeError, ValueError):
                confidence = 0.0

            lines.append(
                OCRLine(
                    text=text,
                    confidence=confidence,
                )
            )

        return lines
