from enum import Enum


class OverlayType(str, Enum):
    PAID_OFFER = "paid_offer"
    ANNOUNCEMENT = "announcement"
    REWARD_FULLSCREEN = "reward_fullscreen"
    CONFIRMATION = "confirmation"
    UNKNOWN = "unknown"
