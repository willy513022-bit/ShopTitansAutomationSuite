from dataclasses import dataclass


@dataclass(frozen=True)
class EnergyPolicy:
    low_energy_ratio: float = 0.30
    high_energy_ratio: float = 0.75
    overflow_risk_ratio: float = 0.90
    cheap_item_value: int = 50_000
    high_item_value: int = 500_000
    allow_small_talk_at_low_energy: bool = True
    allow_energy_speedup: bool = True
    allow_gem_speedup: bool = False


@dataclass(frozen=True)
class QuestPolicy:
    allowed_face_statuses: tuple[str, ...] = (
        "GREEN_HAPPY",
    )


@dataclass(frozen=True)
class MarketPolicy:
    enabled: bool = True
    minimum_gold_reserve: int = 5_000_000
    single_purchase_limit: int = 250_000
    allow_gem_purchase: bool = False
