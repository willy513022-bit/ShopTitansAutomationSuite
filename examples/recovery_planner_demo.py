from recovery.recovery_planner import RecoveryPlanner
from core.screen_state import ScreenState
p=RecoveryPlanner()
for s in [ScreenState.DISCONNECTED,ScreenState.WELCOME_BACK,ScreenState.LIMITED_OFFER,ScreenState.UNKNOWN]:
    print(s.name,"=>",p.plan(s))
