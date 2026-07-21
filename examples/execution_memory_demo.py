from time import sleep
from core.execution_memory import ExecutionMemory
m=ExecutionMemory()
print("Execution Memory Demo")
m.start("LostCity","START_BOSS_QUEST")
print("Start: LostCity -> START_BOSS_QUEST")
sleep(0.2)
r=m.finish(True,"Battle settlement completed")
print(f"Finish: success={r.success}, duration={r.duration:.2f}s")
print(f"History: {m.last().planner} -> {m.last().action}")
