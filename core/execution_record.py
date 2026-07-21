from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExecutionRecord:
    planner:str
    action:str
    started_at:datetime
    finished_at:datetime|None=None
    success:bool|None=None
    reason:str=""
    @property
    def duration(self):
        if self.finished_at is None:
            return None
        return (self.finished_at-self.started_at).total_seconds()
