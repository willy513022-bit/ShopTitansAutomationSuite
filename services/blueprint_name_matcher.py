from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True, slots=True)
class BlueprintNameMatch:
    item_name: str
    score: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "score must be between 0 and 1"
            )


class BlueprintNameMatcher:
    def __init__(
        self,
        item_names: list[str] | tuple[str, ...],
        *,
        minimum_score: float = 0.70,
    ) -> None:
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError(
                "minimum_score must be between 0 and 1"
            )

        self.minimum_score = minimum_score

        unique_names: list[str] = []
        seen: set[str] = set()

        for name in item_names:
            text = str(name).strip()

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)
            unique_names.append(text)

        self.item_names = tuple(unique_names)

    def match(
        self,
        ocr_text: str,
    ) -> BlueprintNameMatch | None:
        if not isinstance(ocr_text, str):
            raise TypeError(
                "ocr_text must be str"
            )

        normalized_query = self.normalize(
            ocr_text
        )

        if not normalized_query:
            return None

        best_name: str | None = None
        best_score = 0.0

        for item_name in self.item_names:
            normalized_candidate = (
                self.normalize(item_name)
            )

            if not normalized_candidate:
                continue

            score = SequenceMatcher(
                None,
                normalized_query,
                normalized_candidate,
            ).ratio()

            if score > best_score:
                best_score = score
                best_name = item_name

        if best_name is None:
            return None

        if best_score < self.minimum_score:
            return None

        return BlueprintNameMatch(
            item_name=best_name,
            score=best_score,
        )

    @staticmethod
    def normalize(
        value: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "value must be str"
            )

        value = unicodedata.normalize(
            "NFKD",
            value,
        )

        value = (
            value
            .replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
        )

        value = value.lower()

        # Apostrophe 對名稱身份通常沒有必要，
        # 移除後：
        #
        # Queen's
        # Queens
        #
        # 可以更容易互相比對。
        value = value.replace(
            "'",
            "",
        )

        value = re.sub(
            r"[^a-z0-9]+",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()