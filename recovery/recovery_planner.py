from recovery.popup_rules import POPUP_RULES

class RecoveryPlanner:
    def plan(self, screen_state):
        rule = POPUP_RULES.get(screen_state)
        if rule is None:
            return None
        return {
            "action": rule["action"],
            "expected": rule["expected"],
            "safety": rule.get("safety"),
        }
