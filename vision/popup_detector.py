from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Tuple, Union

import cv2
import numpy as np

from vision.popup_models import PopupDetection, PopupType
from vision.template_matcher import ImageInput, TemplateMatcher


@dataclass(frozen=True)
class PopupTemplate:
    template_id: str
    image: np.ndarray

    def __post_init__(self) -> None:
        if not self.template_id.strip():
            raise ValueError("template_id is required")
        if not isinstance(self.image, np.ndarray) or self.image.size == 0:
            raise ValueError("image must be a non-empty numpy array")


class PopupDetector:
    """Registry-based multi-template popup detector.

    The detector reports visual facts only. Semantic meaning, priority, and
    runtime actions are handled by ``PopupParser`` and ``PopupPriorityResolver``.
    """

    def __init__(
        self,
        templates: Optional[
            Mapping[PopupType | str, Iterable[PopupTemplate]]
        ] = None,
        matcher: Optional[TemplateMatcher] = None,
    ) -> None:
        self.matcher = matcher or TemplateMatcher()
        self.templates: Dict[PopupType, list[PopupTemplate]] = {}
        for popup_type, variants in (templates or {}).items():
            for variant in variants:
                self.register(popup_type, variant)

    def register(
        self,
        popup_type: PopupType | str,
        template: PopupTemplate,
    ) -> None:
        normalized = self._normalize_popup_type(popup_type)
        bucket = self.templates.setdefault(normalized, [])
        if any(item.template_id == template.template_id for item in bucket):
            raise ValueError(
                f"Duplicate popup template id for {normalized.value}: "
                f"{template.template_id!r}"
            )
        bucket.append(template)

    def register_file(
        self,
        popup_type: PopupType | str,
        path: Union[str, Path],
        template_id: Optional[str] = None,
    ) -> None:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Unable to load popup template: {path}")
        resolved_id = template_id or Path(path).stem
        self.register(
            popup_type,
            PopupTemplate(template_id=resolved_id, image=image),
        )

    def detect(self, screenshot: ImageInput) -> Tuple[PopupDetection, ...]:
        detections = []
        for popup_type, variants in self.templates.items():
            winner: Optional[PopupDetection] = None
            for variant in variants:
                result = self.matcher.match(
                    screenshot,
                    variant.image,
                    template_name=f"popup:{popup_type.value}:{variant.template_id}",
                )
                if not result.matched:
                    continue
                candidate = PopupDetection(
                    popup_type=popup_type,
                    confidence=result.confidence,
                    template_id=variant.template_id,
                    location=result.location,
                    size=result.size,
                )
                if winner is None or candidate.confidence > winner.confidence:
                    winner = candidate
            if winner is not None:
                detections.append(winner)

        detections.sort(key=lambda item: item.confidence, reverse=True)
        return tuple(detections)

    def detect_best(self, screenshot: ImageInput) -> Optional[PopupDetection]:
        detections = self.detect(screenshot)
        return detections[0] if detections else None

    @staticmethod
    def _normalize_popup_type(popup_type: PopupType | str) -> PopupType:
        if isinstance(popup_type, PopupType):
            return popup_type
        try:
            return PopupType(str(popup_type).strip().lower())
        except ValueError as exc:
            raise ValueError(f"Unsupported popup type: {popup_type!r}") from exc
