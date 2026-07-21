
from dataclasses import dataclass
@dataclass
class WindowInfo:
    title:str
    left:int
    top:int
    width:int
    height:int

class WindowManager:
    def __init__(self,window=None):
        self._window=window
    def get_window(self):
        return self._window
