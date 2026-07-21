from dataclasses import dataclass
from executor.keybinds import KeybindAction, KeybindMap

@dataclass(frozen=True)
class KeyboardExecutionResult:
    action: KeybindAction
    key: str
    executed: bool
    reason: str

class DryRunKeyboardExecutor:
    def __init__(self, keybind_map: KeybindMap | None = None) -> None:
        self.keybind_map = keybind_map or KeybindMap()

    def execute(self, action: KeybindAction) -> KeyboardExecutionResult:
        key = self.keybind_map.get(action)
        print(f"[DRY RUN] key={key!r} action={action.value}")
        return KeyboardExecutionResult(
            action=action,
            key=key,
            executed=False,
            reason="Dry Run 模式，不會真的送出鍵盤輸入",
        )
