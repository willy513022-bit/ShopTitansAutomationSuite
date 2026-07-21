from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

import numpy as np

from vision.match_result import MatchResult
from vision.template_matcher import TemplateMatcher


@dataclass(frozen=True)
class ScreenDetection:
    screen_name: str
    confidence: float
    match: MatchResult


class ScreenDetector:
    def __init__(
        self,
        matcher: Optional[TemplateMatcher] = None,
        templates: Optional[Dict[str, np.ndarray]] = None,
    ):
        self.matcher = matcher or TemplateMatcher()
        self.templates: Dict[str, np.ndarray] = dict(templates or {})

    def register_template(self, screen_name: str, template: np.ndarray) -> None:
        if not screen_name:
            raise ValueError("screen_name is required")
        self.templates[screen_name] = template.copy()

    def detect(self, screenshot: np.ndarray) -> Optional[ScreenDetection]:
        winner: Optional[ScreenDetection] = None

        for screen_name, template in self.templates.items():
            result = self.matcher.match(
                screenshot=screenshot,
                template=template,
                template_name=screen_name,
            )
            if not result.matched:
                continue

            candidate = ScreenDetection(
                screen_name=screen_name,
                confidence=result.confidence,
                match=result,
            )
            if winner is None or candidate.confidence > winner.confidence:
                winner = candidate

        return winner

    def detect_ranked(self, screenshot: np.ndarray) -> Tuple[ScreenDetection, ...]:
        results = []

        for screen_name, template in self.templates.items():
            result = self.matcher.match(
                screenshot=screenshot,
                template=template,
                template_name=screen_name,
            )
            if result.matched:
                results.append(
                    ScreenDetection(
                        screen_name=screen_name,
                        confidence=result.confidence,
                        match=result,
                    )
                )

        results.sort(key=lambda item: item.confidence, reverse=True)
        return tuple(results)
