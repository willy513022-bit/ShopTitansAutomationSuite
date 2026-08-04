from __future__ import annotations

from collections.abc import Callable
from typing import Optional, Protocol

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from services.blueprint_progress_parser import (
    BlueprintProgressParser,
)
from vision.blueprint_progress_models import (
    BlueprintProgressDetection,
    BlueprintProgressOCRResult,
    ImageRegion,
)
from vision.blueprint_progress_regions import (
    BlueprintProgressRegionLocator,
)


class BlueprintProgressOCRReader(Protocol):
    """
    可替換的 OCR 介面。

    正式環境使用 RapidOCR；
    單元測試可以放入假的 OCR。
    """

    def read(
        self,
        image: np.ndarray,
    ) -> BlueprintProgressOCRResult:
        ...


class RapidBlueprintProgressOCR:
    """
    Blueprint 進度專用 RapidOCR 包裝器。
    """

    def __init__(
        self,
        engine: Optional[Callable] = None,
    ) -> None:
        self._engine = engine or RapidOCR()

    def read(
        self,
        image: np.ndarray,
    ) -> BlueprintProgressOCRResult:
        if image is None or image.size == 0:
            return BlueprintProgressOCRResult(
                text="",
                confidence=0.0,
            )

        result, _ = self._engine(image)

        if not result:
            return BlueprintProgressOCRResult(
                text="",
                confidence=0.0,
            )

        texts: list[str] = []
        confidences: list[float] = []

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

            confidence = min(
                1.0,
                max(0.0, confidence),
            )

            texts.append(text)
            confidences.append(confidence)

        if not texts:
            return BlueprintProgressOCRResult(
                text="",
                confidence=0.0,
            )

        return BlueprintProgressOCRResult(
            text=" ".join(texts),
            confidence=(
                sum(confidences)
                / len(confidences)
                if confidences
                else 0.0
            ),
        )


class BlueprintProgressDetector:
    """
    從指定製作卡片中讀取 Blueprint 里程碑進度。

    第一版不負責尋找卡片；
    呼叫端必須提供 card_region。
    """

    def __init__(
        self,
        *,
        region_locator: (
            BlueprintProgressRegionLocator
            | None
        ) = None,
        ocr_reader: (
            BlueprintProgressOCRReader
            | None
        ) = None,
        parser: BlueprintProgressParser
        | None = None,
        minimum_confidence: float = 0.0,
        upscale: float = 4.0,
    ) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError(
                "minimum_confidence must be "
                "between 0 and 1"
            )

        if upscale <= 0:
            raise ValueError(
                "upscale must be greater than 0"
            )

        self.region_locator = (
            region_locator
            or BlueprintProgressRegionLocator()
        )

        self.ocr_reader = (
            ocr_reader
            or RapidBlueprintProgressOCR()
        )

        self.parser = (
            parser
            or BlueprintProgressParser()
        )

        self.minimum_confidence = (
            minimum_confidence
        )

        self.upscale = upscale

    def detect(
        self,
        image: np.ndarray,
        card_region: ImageRegion,
    ) -> BlueprintProgressDetection:
        self._validate_image(image)

        if not isinstance(card_region, ImageRegion):
            raise TypeError(
                "card_region must be ImageRegion"
            )

        progress_region = (
            self.region_locator.locate(
                card_region
            )
        )

        crop = self._crop(
            image=image,
            region=progress_region,
        )

        prepared = self._prepare_image(crop)

        ocr_result = self.ocr_reader.read(
            prepared
        )

        parsed = None

        if (
            ocr_result.confidence
            >= self.minimum_confidence
        ):
            parsed = self.parser.parse(
                ocr_result.text
            )

        return BlueprintProgressDetection(
            card_region=card_region,
            progress_region=progress_region,
            ocr_text=ocr_result.text,
            ocr_confidence=(
                ocr_result.confidence
            ),
            parsed=parsed,
        )

    @staticmethod
    def _validate_image(
        image: np.ndarray,
    ) -> None:
        if not isinstance(image, np.ndarray):
            raise TypeError(
                "image must be numpy.ndarray"
            )

        if image.size == 0:
            raise ValueError(
                "image cannot be empty"
            )

        if image.ndim not in (2, 3):
            raise ValueError(
                "image must be grayscale or BGR"
            )

    @staticmethod
    def _crop(
        *,
        image: np.ndarray,
        region: ImageRegion,
    ) -> np.ndarray:
        image_height, image_width = (
            image.shape[:2]
        )

        left = max(0, region.left)
        top = max(0, region.top)

        right = min(
            image_width,
            region.right,
        )

        bottom = min(
            image_height,
            region.bottom,
        )

        if right <= left or bottom <= top:
            return np.empty(
                (0, 0),
                dtype=image.dtype,
            )

        return image[
            top:bottom,
            left:right,
        ].copy()

    def _prepare_image(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        if image.size == 0:
            return image

        enlarged = cv2.resize(
            image,
            None,
            fx=self.upscale,
            fy=self.upscale,
            interpolation=cv2.INTER_CUBIC,
        )

        if enlarged.ndim == 3:
            grayscale = cv2.cvtColor(
                enlarged,
                cv2.COLOR_BGR2GRAY,
            )
        else:
            grayscale = enlarged

        # 局部對比增強，對白色數字與深色背景通常較有效。
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        enhanced = clahe.apply(
            grayscale
        )

        return enhanced