
from datetime import datetime, timedelta

class CooldownManager:
    def __init__(self):
        self._cd={}
    def start(self,key,seconds,reason=""):
        self._cd[key]={"until":datetime.now()+timedelta(seconds=seconds),"reason":reason}
    def is_ready(self,key):
        return key not in self._cd or datetime.now()>=self._cd[key]["until"]
    def remaining(self,key):
        if self.is_ready(key):
            return 0
        return max(0,int((self._cd[key]["until"]-datetime.now()).total_seconds()))
    def clear(self,key):
        self._cd.pop(key,None)
    def clear_all(self):
        self._cd.clear()
