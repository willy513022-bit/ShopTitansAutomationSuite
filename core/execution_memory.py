from datetime import datetime
from .execution_record import ExecutionRecord

class ExecutionMemory:
    def __init__(self):
        self._current=None
        self._history=[]
    def start(self, planner, action):
        self._current=ExecutionRecord(planner,action,datetime.now())
        return self._current
    def finish(self, success=True, reason=""):
        if not self._current:
            return None
        self._current.finished_at=datetime.now()
        self._current.success=success
        self._current.reason=reason
        self._history.append(self._current)
        r=self._current
        self._current=None
        return r
    def current(self): return self._current
    def last(self): return self._history[-1] if self._history else None
    def history(self,limit=None):
        return self._history if limit is None else self._history[-limit:]
    def clear(self):
        self._current=None
        self._history.clear()
