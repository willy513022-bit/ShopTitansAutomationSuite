from enum import Enum, auto

class ScreenState(Enum):
    UNKNOWN = auto()
    TOWN = auto()
    LOADING = auto()
    DISCONNECTED = auto()
    WELCOME_BACK = auto()
    LIMITED_OFFER = auto()
