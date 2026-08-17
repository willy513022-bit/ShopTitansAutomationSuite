from __future__ import annotations

from collections.abc import Callable
from typing import Optional, Protocol

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from services.blueprint_name_matcher import (
    BlueprintNameMatcher,
)
from vision.blueprint_name_models import (
    BlueprintNameDetection,
    BlueprintNameOCRResult,
)
from vision.blueprint_name_regions import (
    BlueprintNameRegionLocator,
)
from vision.blueprint_progress_models import (
    ImageRegion,
)


class BlueprintNameOCRReader(Protocol):
    def read(
        self,
        image: np.ndarray,
    ) -> BlueprintNameOCRResult:
        ...


class RapidBlueprintNameOCR:
    def __init__(
        self,
        engine: Optional[Callable] = None,
    ) -> None:
        self._engine = engine or RapidOCR()

    def read(
        self,
        image: np.ndarray,
    ) -> BlueprintNameOCRResult:
        if image is None or image.size == 0:
            return BlueprintNameOCRResult(
                text="",
                confidence=0.0,
            )

        result, _ = self._engine(image)

        if not result:
            return BlueprintNameOCRResult(
                text="",
                confidence=0.0,
            )

        texts: list[str] = []
        confidences: list[float] = []

        for item in result:
            if len(item) < 3:
                continue

            text = str(
                item[1]
            ).strip()

            if not text:
                continue

            try:
                confidence = float(
                    item[2]
                )
            except (
                TypeError,
                ValueError,
            ):
                confidence = 0.0

            confidence = min(
                1.0,
                max(
                    0.0,
                    confidence,
                ),
            )

            texts.append(text)
            confidences.append(
                confidence
            )

        if not texts:
            return BlueprintNameOCRResult(
                text="",
                confidence=0.0,
            )

        return BlueprintNameOCRResult(
            text=" ".join(texts),
            confidence=(
                sum(confidences)
                / len(confidences)
            ),
        )


class BlueprintNameDetector:
    def __init__(
        self,
        *,
        region_locator: (
            BlueprintNameRegionLocator
            | None
        ) = None,
        ocr_reader: (
            BlueprintNameOCRReader
            | None
        ) = None,
        matcher: (
            BlueprintNameMatcher
            | None
        ) = None,
        minimum_ocr_confidence: float = 0.0,
        upscale: float = 4.0,
    ) -> None:
        if not (
            0.0
            <= minimum_ocr_confidence
            <= 1.0
        ):
            raise ValueError(
                "minimum_ocr_confidence must be "
                "between 0 and 1"
            )

        if upscale <= 0:
            raise ValueError(
                "upscale must be greater than 0"
            )

        self.region_locator = (
            region_locator
            or BlueprintNameRegionLocator()
        )

        self.ocr_reader = (
            ocr_reader
            or RapidBlueprintNameOCR()
        )

        self.matcher = matcher

        self.minimum_ocr_confidence = (
            minimum_ocr_confidence
        )

        self.upscale = upscale

    def detect(
        self,
        image: np.ndarray,
        card_region: ImageRegion,
    ) -> BlueprintNameDetection:
        self._validate_image(
            image
        )

        if not isinstance(
            card_region,
            ImageRegion,
        ):
            raise TypeError(
                "card_region must be ImageRegion"
            )

        name_region = (
            self.region_locator.locate(
                card_region
            )
        )

        crop = self._crop(
            image=image,
            region=name_region,
        )

        prepared = self._prepare_image(
            crop
        )

        ocr_result = (
            self.ocr_reader.read(
                prepared
            )
        )

        item_name = None
        match_score = None

        if (
            ocr_result.confidence
            >= self.minimum_ocr_confidence
        ):
            if self.matcher is None:
                cleaned = (
                    ocr_result.text.strip()
                )

                if cleaned:
                    item_name = cleaned

            else:
                match = self.matcher.match(
                    ocr_result.text
                )

                if match is not None:
                    item_name = (
                        match.item_name
                    )

                    match_score = (
                        match.score
                    )

        return BlueprintNameDetection(
            card_region=card_region,
            name_region=name_region,
            ocr_text=ocr_result.text,
            ocr_confidence=(
                ocr_result.confidence
            ),
            item_name=item_name,
            match_score=match_score,
        )

    @staticmethod
    def _validate_image(
        image: np.ndarray,
    ) -> None:
        if not isinstance(
            image,
            np.ndarray,
        ):
            raise TypeError(
                "image must be numpy.ndarray"
            )

        if image.size == 0:
            raise ValueError(
                "image cannot be empty"
            )

        if image.ndim not in (
            2,
            3,
        ):
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

        left = max(
            0,
            region.left,
        )

        top = max(
            0,
            region.top,
        )

        right = min(
            image_width,
            region.right,
        )

        bottom = min(
            image_height,
            region.bottom,
        )

        if (
            right <= left
            or bottom <= top
        ):
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

        # 名稱是淺色文字 + 紫紅色背景。
        # 第一版先保留 BGR 彩色資訊給 RapidOCR。
        #
        # Progress OCR 適合灰階 CLAHE，
        # Name OCR 不一定，所以先不要共用處理。
        return enlarged