from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class MatchResult:
    template_name: str
    confidence: float
    location: Optional[Tuple[int, int]] = None
    size: Optional[Tuple[int, int]] = None

    @property
    def matched(self) -> bool:
        return self.location is not None
