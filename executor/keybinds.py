from dataclasses import dataclass, field
from enum import Enum

class KeybindAction(str, Enum):
    CRAFT_MENU = "craft_menu"
    INVENTORY = "inventory"
    QUEST_MENU = "quest_menu"
    MARKET = "market"
    SMALL_TALK = "small_talk"
    SURCHARGE = "surcharge"
    DISCOUNT = "discount"
    SELL = "sell"
    REFUSE = "refuse"
    WAIT = "wait"
    CLAIM_CRAFT_QUEST = "claim_craft_quest"
    SWITCH_CRAFT_FUSION = "switch_craft_fusion"

@dataclass
class KeybindMap:
    bindings: dict[KeybindAction, str] = field(default_factory=lambda: {
        KeybindAction.CRAFT_MENU: "m",
        KeybindAction.INVENTORY: "3",
        KeybindAction.QUEST_MENU: "space",
        KeybindAction.MARKET: "2",
        KeybindAction.SMALL_TALK: "num3",
        KeybindAction.SURCHARGE: "decimal",
        KeybindAction.DISCOUNT: "divide",
        KeybindAction.SELL: "enter",
        KeybindAction.REFUSE: "add",
        KeybindAction.WAIT: "x",
        KeybindAction.CLAIM_CRAFT_QUEST: "space",
        KeybindAction.SWITCH_CRAFT_FUSION: "tab",
    })

    def get(self, action: KeybindAction) -> str:
        return self.bindings[action]
