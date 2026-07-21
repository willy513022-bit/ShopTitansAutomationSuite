from core.screen_state import ScreenState
from recovery.popup_rules import POPUP_RULES

for s in [ScreenState.DISCONNECTED, ScreenState.WELCOME_BACK, ScreenState.LIMITED_OFFER]:
    print(s.name, "->", POPUP_RULES[s])
