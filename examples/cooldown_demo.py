
import time
from core.cooldown import CooldownManager
c=CooldownManager()
print("Loop1: Collection executes")
c.start("Collection",3,"Collected inventory")
for i in range(1,5):
    print(f"Loop{i+1}: Collection ready={c.is_ready('Collection')} remaining={c.remaining('Collection')}s")
    time.sleep(1)
