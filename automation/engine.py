from automation.logger import log
from automation.state import BotState
class AutomationEngine:
    def __init__(self):self.state=BotState.STOPPED
    def start(self):log("INFO","Bot 正在啟動");self.state=BotState.RUNNING;log("INFO","Bot 已開始執行")
    def pause(self):self.state=BotState.PAUSED;log("INFO","Bot 已暫停")
    def stop(self):log("INFO","Bot 正在停止");self.state=BotState.STOPPED;log("INFO","Bot 已停止")
