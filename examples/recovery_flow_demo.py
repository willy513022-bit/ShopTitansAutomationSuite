from recovery.recovery_flow import RecoveryFlow
from core.screen_state import ScreenState

flow=RecoveryFlow()

for s in [ScreenState.DISCONNECTED,ScreenState.WELCOME_BACK,ScreenState.LIMITED_OFFER,ScreenState.UNKNOWN]:
    print(s.name,"=>",flow.execute(s))
