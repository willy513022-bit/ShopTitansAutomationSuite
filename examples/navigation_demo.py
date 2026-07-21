from navigation import (
    NavigationStateTracker,
    NavigationValidator,
    Navigator,
    Screen,
    build_default_screen_graph,
)


def main() -> None:
    tracker = NavigationStateTracker()
    tracker.update(Screen.SHOP, 0.98)

    navigator = Navigator(
        build_default_screen_graph(),
        tracker,
    )
    validator = NavigationValidator()

    plan = navigator.plan(Screen.FUSION)

    print("Navigation Engine V1 Demo")
    print("current_screen =", plan.start.value)
    print("target_screen =", plan.target.value)
    print("route =", " -> ".join(screen.value for screen in plan.screens()))
    print("total_cost =", plan.total_cost)

    for transition in plan.transitions:
        print(
            "execute =",
            transition.action.value,
            "| expected =",
            transition.target.value,
        )
        result = validator.validate_transition(
            transition,
            observed=transition.target,
            confidence=0.95,
        )
        print(
            "validated =",
            result.success,
            "| reason =",
            result.reason,
        )
        tracker.update(transition.target, 0.95)

    print("final_screen =", tracker.current_screen.value)


if __name__ == "__main__":
    main()
