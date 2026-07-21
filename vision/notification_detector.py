from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple

import numpy as np

from vision.match_result import MatchResult
from vision.notification_models import NotificationCategory, NotificationDetection
from vision.template_matcher import TemplateMatcher


@dataclass(frozen=True)
class NotificationTemplateSet:
    """Templates used for one notification category."""

    icon: np.ndarray
    badges: Mapping[str, np.ndarray]

    def __post_init__(self) -> None:
        if not isinstance(self.icon, np.ndarray) or self.icon.size == 0:
            raise ValueError("icon must be a non-empty numpy array")
        if not self.badges:
            raise ValueError("at least one badge template is required")
        for badge, template in self.badges.items():
            if badge != "+" and not str(badge).isdigit():
                raise ValueError("badge template keys must be '+' or integer strings")
            if not isinstance(template, np.ndarray) or template.size == 0:
                raise ValueError(f"badge template {badge!r} must be a non-empty array")


class NotificationDetector:
    """Generic icon + badge template detector.

    This class detects visual facts only. Category-specific meaning of ``+``
    is handled by :class:`vision.notification_parser.NotificationParser`.
    """

    def __init__(
        self,
        templates: Optional[
            Mapping[NotificationCategory | str, NotificationTemplateSet]
        ] = None,
        matcher: Optional[TemplateMatcher] = None,
    ) -> None:
        self.matcher = matcher or TemplateMatcher()
        self.templates: Dict[NotificationCategory, NotificationTemplateSet] = {}
        for category, template_set in (templates or {}).items():
            self.register(category, template_set)

    def register(
        self,
        category: NotificationCategory | str,
        template_set: NotificationTemplateSet,
    ) -> None:
        normalized = self._normalize_category(category)
        self.templates[normalized] = template_set

    def detect(self, screenshot: np.ndarray) -> Tuple[NotificationDetection, ...]:
        if not isinstance(screenshot, np.ndarray) or screenshot.size == 0:
            raise ValueError("screenshot must be a non-empty numpy array")

        detections = []
        for category, template_set in self.templates.items():
            icon_match = self.matcher.match(
                screenshot,
                template_set.icon,
                template_name=f"notification:{category.value}:icon",
            )
            if not icon_match.matched:
                continue

            badge, badge_match = self._best_badge_match(
                screenshot=screenshot,
                category=category,
                badges=template_set.badges,
            )
            if badge is None or badge_match is None:
                continue

            # Both pieces must be reliable. Taking the minimum prevents a high
            # icon score from hiding a weak badge match.
            confidence = min(icon_match.confidence, badge_match.confidence)
            detections.append(
                NotificationDetection(
                    category=category,
                    badge=badge,
                    confidence=confidence,
                    icon_confidence=icon_match.confidence,
                    badge_confidence=badge_match.confidence,
                    icon_location=icon_match.location,
                    badge_location=badge_match.location,
                )
            )

        detections.sort(key=lambda item: item.confidence, reverse=True)
        return tuple(detections)

    def detect_best(self, screenshot: np.ndarray) -> Optional[NotificationDetection]:
        detections = self.detect(screenshot)
        return detections[0] if detections else None

    def _best_badge_match(
        self,
        screenshot: np.ndarray,
        category: NotificationCategory,
        badges: Mapping[str, np.ndarray],
    ) -> tuple[Optional[str], Optional[MatchResult]]:
        winner_badge: Optional[str] = None
        winner_match: Optional[MatchResult] = None

        for badge, template in badges.items():
            result = self.matcher.match(
                screenshot,
                template,
                template_name=f"notification:{category.value}:badge:{badge}",
            )
            if not result.matched:
                continue
            if winner_match is None or result.confidence > winner_match.confidence:
                winner_badge = str(badge)
                winner_match = result

        return winner_badge, winner_match

    @staticmethod
    def _normalize_category(
        category: NotificationCategory | str,
    ) -> NotificationCategory:
        if isinstance(category, NotificationCategory):
            return category
        try:
            return NotificationCategory(str(category).strip().lower())
        except ValueError as exc:
            raise ValueError(f"Unsupported notification category: {category!r}") from exc
