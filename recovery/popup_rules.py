from core.screen_state import ScreenState

POPUP_RULES = {
    ScreenState.DISCONNECTED: {
        "action":"RECONNECT",
        "expected":ScreenState.LOADING,
    },
    ScreenState.WELCOME_BACK: {
        "action":"CLOSE_POPUP",
        "expected":ScreenState.TOWN,
    },
    ScreenState.LIMITED_OFFER: {
        "action":"CLOSE_POPUP",
        "expected":ScreenState.TOWN,
        "safety":"Never purchase offers",
    },
}
