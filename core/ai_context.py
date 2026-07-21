from dataclasses import dataclass, field
from typing import Any

@dataclass
class AIContext:
    game_state: Any=None
    task_lock: Any=None
    execution_memory: Any=None
    cooldown_manager: Any=None
    screen_state: Any=None
    settings: dict=field(default_factory=dict)
    statistics: dict=field(default_factory=dict)

    def summary(self):
        return {"screen_state":self.screen_state,"settings":len(self.settings),"statistics":len(self.statistics),"has_game_state":self.game_state is not None}
