from ai.strategy_engine import (
    StrategyEngine,
)
from state.game_state_builder import (
    GameStateBuilder,
)
from state.live_energy_state_provider import (
    LiveEnergyStateProvider,
)


def main() -> None:
    print("Live Energy Bridge 測試")
    print("=" * 70)

    builder = GameStateBuilder(
        providers=[
            LiveEnergyStateProvider(
                minimum_confidence=0.20
            )
        ]
    )

    try:
        state = builder.build()

    except Exception as error:
        print("Bridge 失敗：", error)
        return

    print(
        "energy：",
        state.energy.current,
        "/",
        state.energy.maximum,
    )

    if "live_energy_error" in state.metadata:
        print(
            "error：",
            state.metadata[
                "live_energy_error"
            ],
        )

    print(
        "raw_text：",
        repr(
            state.metadata.get(
                "live_energy_raw_text",
                "",
            )
        ),
    )

    action = StrategyEngine().decide(
        state
    )

    print()
    print("AI Decision")
    print("-" * 70)
    print(
        "action：",
        action.action_type.value,
    )
    print(
        "score：",
        action.score,
    )
    print(
        "reason：",
        action.reason,
    )


if __name__ == "__main__":
    main()
