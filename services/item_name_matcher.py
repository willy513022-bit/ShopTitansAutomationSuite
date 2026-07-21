import re
from dataclasses import dataclass
from rapidfuzz import fuzz, process
from services.game_data_service import GameDataService, game_data_service

@dataclass(frozen=True)
class ItemNameMatch:
    raw_text: str
    cleaned_text: str
    item_id: str | None
    matched_name: str | None
    score: float

class ItemNameMatcher:
    def __init__(self, game_data: GameDataService = game_data_service, minimum_score: float = 70.0):
        self.game_data = game_data
        self.minimum_score = minimum_score
        self._names = [item.name for item in self.game_data.get_all()]

    def match(self, raw_text: str) -> ItemNameMatch:
        cleaned = self._clean_text(raw_text)
        if not cleaned: return ItemNameMatch(raw_text, cleaned, None, None, 0.0)
        result = process.extractOne(cleaned, self._names, scorer=fuzz.WRatio)
        if result is None: return ItemNameMatch(raw_text, cleaned, None, None, 0.0)
        matched_name, score, _ = result
        if score < self.minimum_score: return ItemNameMatch(raw_text, cleaned, None, None, float(score))
        item = self.game_data.get_by_name(matched_name)
        return ItemNameMatch(raw_text, cleaned, item.item_id if item else None, matched_name, float(score))

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"^[^A-Za-z0-9]+", "", text.strip())
        text = re.sub(r"[^A-Za-z0-9]+$", "", text)
        return re.sub(r"\s+", " ", text).strip()

item_name_matcher = ItemNameMatcher()
