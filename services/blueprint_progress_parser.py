from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class ParsedBlueprintProgress:
    """
    從 OCR 文字解析出的藍圖里程碑進度。

    例如：
        raw_text="10/15"
        current_progress=10
        current_target=15
    """

    raw_text: str
    normalized_text: str
    current_progress: int
    current_target: int

    def __post_init__(self) -> None:
        if self.current_progress < 0:
            raise ValueError(
                "current_progress cannot be negative"
            )

        if self.current_target <= 0:
            raise ValueError(
                "current_target must be greater than 0"
            )

        if self.current_progress > self.current_target:
            raise ValueError(
                "current_progress cannot exceed current_target"
            )

    @property
    def remaining(self) -> int:
        return self.current_target - self.current_progress

    @property
    def complete(self) -> bool:
        return self.current_progress == self.current_target


class BlueprintProgressParser:
    """
    將 OCR 輸出的文字解析為 current / target。

    支援進度數字區域中的常見 OCR 誤判：

        O、o -> 0
        I、l、| -> 1
        ／、\\ -> /

    重要：
        不會對整段英文文字做 O/o/I/l 替換，
        避免把 Progress 變成 Pr0gress。

    Parser 採保守策略：
        無法明確判斷時回傳 None，不強行猜測。
    """

    # 只擷取可能形成「左值 / 右值」的區段。
    # 左右值允許數字以及常見 OCR 誤判字元。
    _CANDIDATE_PATTERN = re.compile(
        r"(?<![0-9A-Za-z])"
        r"(?P<current>[0-9OoIl|]{1,4})"
        r"\s*[/／\\]\s*"
        r"(?P<target>[0-9OoIl|]{1,4})"
        r"(?![0-9A-Za-z])"
    )

    _DIGIT_REPLACEMENTS = str.maketrans(
        {
            "O": "0",
            "o": "0",
            "I": "1",
            "l": "1",
            "|": "1",
        }
    )

    _SLASH_REPLACEMENTS = str.maketrans(
        {
            "／": "/",
            "\\": "/",
        }
    )

    def parse(
        self,
        text: str,
    ) -> Optional[ParsedBlueprintProgress]:
        """
        解析 OCR 文字。

        成功：
            ParsedBlueprintProgress

        失敗：
            None
        """

        if not isinstance(text, str):
            raise TypeError("text must be str")

        raw_text = text
        normalized = self.normalize(text)

        if not normalized:
            return None

        matches = tuple(
            self._CANDIDATE_PATTERN.finditer(normalized)
        )

        # 同一段 OCR 文字出現多組進度時，
        # 無法判斷哪一組屬於目標物品。
        if len(matches) != 1:
            return None

        match = matches[0]

        current_text = self._normalize_digit_token(
            match.group("current")
        )
        target_text = self._normalize_digit_token(
            match.group("target")
        )

        if not current_text.isdigit():
            return None

        if not target_text.isdigit():
            return None

        current_progress = int(current_text)
        current_target = int(target_text)

        if current_target <= 0:
            return None

        if current_progress > current_target:
            return None

        normalized_text = self._replace_match_with_digits(
            text=normalized,
            match=match,
            current=current_text,
            target=target_text,
        )

        return ParsedBlueprintProgress(
            raw_text=raw_text,
            normalized_text=normalized_text,
            current_progress=current_progress,
            current_target=current_target,
        )

    def parse_required(
        self,
        text: str,
    ) -> ParsedBlueprintProgress:
        """
        和 parse() 相同，但解析失敗時拋出 ValueError。

        適合用於已確認該區域應包含進度的流程。
        """

        result = self.parse(text)

        if result is None:
            raise ValueError(
                "Unable to parse blueprint progress "
                f"from text: {text!r}"
            )

        return result

    @classmethod
    def normalize(
        cls,
        text: str,
    ) -> str:
        """
        正規化換行、空白及斜線。

        不在這裡全域替換 O/o/I/l，
        因為這些字元可能屬於正常英文單字。
        """

        if not isinstance(text, str):
            raise TypeError("text must be str")

        normalized = text.translate(
            cls._SLASH_REPLACEMENTS
        )

        normalized = normalized.replace(
            "\r",
            " ",
        )
        normalized = normalized.replace(
            "\n",
            " ",
        )
        normalized = normalized.replace(
            "\t",
            " ",
        )

        normalized = " ".join(
            normalized.split()
        )

        return normalized.strip()

    @classmethod
    def _normalize_digit_token(
        cls,
        token: str,
    ) -> str:
        """
        只在進度候選值內修正 OCR 誤判。
        """

        return token.translate(
            cls._DIGIT_REPLACEMENTS
        )

    @staticmethod
    def _replace_match_with_digits(
        *,
        text: str,
        match: re.Match[str],
        current: str,
        target: str,
    ) -> str:
        """
        保留其餘文字，只把已確認的進度區段改成標準格式。
        """

        replacement = f"{current} / {target}"

        return (
            text[: match.start()]
            + replacement
            + text[match.end() :]
        )