
class ClickExecutor:
    def __init__(self,dry_run=True):
        self.dry_run=dry_run
    def click(self,x,y):
        return {"mode":"DRY_RUN" if self.dry_run else "LIVE","x":x,"y":y}
