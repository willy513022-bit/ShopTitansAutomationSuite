class RecoveryExecutor:
    def __init__(self, dry_run=True):
        self.dry_run=dry_run
    def execute(self, decision):
        if decision is None:
            return {"executed":False,"reason":"NO_DECISION"}
        if self.dry_run:
            return {"executed":True,"mode":"DRY_RUN","action":decision["action"]}
        # placeholder for real mouse/adb integration
        return {"executed":True,"mode":"LIVE","action":decision["action"]}
