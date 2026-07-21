from recovery.recovery_planner import RecoveryPlanner

class RecoveryFlow:
    def __init__(self, validator=None, max_retry=3):
        self.planner=RecoveryPlanner()
        self.validator=validator
        self.max_retry=max_retry

    def execute(self, screen_state):
        decision=self.planner.plan(screen_state)
        if decision is None:
            return {"status":"NO_RULE","decision":None}

        for attempt in range(1,self.max_retry+1):
            ok=True if self.validator is None else self.validator(decision)
            if ok:
                return {
                    "status":"RECOVERED",
                    "attempt":attempt,
                    "decision":decision
                }
        return {
            "status":"FAILED",
            "attempt":self.max_retry,
            "decision":decision
        }
