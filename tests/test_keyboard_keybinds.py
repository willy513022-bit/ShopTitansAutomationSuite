from executor.keybinds import KeybindAction, KeybindMap
from executor.keyboard_executor import DryRunKeyboardExecutor

def main():
    print("Keyboard Keybinds 測試")
    print("=" * 72)
    keybinds = KeybindMap()
    expected = {
        KeybindAction.CRAFT_MENU: "m",
        KeybindAction.INVENTORY: "3",
        KeybindAction.QUEST_MENU: "space",
        KeybindAction.SMALL_TALK: "num3",
        KeybindAction.SURCHARGE: "decimal",
        KeybindAction.DISCOUNT: "divide",
        KeybindAction.SELL: "enter",
        KeybindAction.REFUSE: "add",
        KeybindAction.WAIT: "x",
    }
    for action, key in expected.items():
        actual = keybinds.get(action)
        print(f"{action.value:<24} {actual}")
        assert actual == key

    result = DryRunKeyboardExecutor(keybinds).execute(KeybindAction.SMALL_TALK)
    assert result.executed is False
    assert result.key == "num3"
    print("測試通過")

if __name__ == "__main__":
    main()
