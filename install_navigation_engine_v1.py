from pathlib import Path


REQUIRED = [
    Path("navigation/screen.py"),
    Path("navigation/transition.py"),
    Path("navigation/graph.py"),
    Path("navigation/state_tracker.py"),
    Path("navigation/navigator.py"),
    Path("navigation/validator.py"),
    Path("vision/state.py"),
    Path("data/navigation/default_screen_graph.json"),
]


def main() -> None:
    missing = [str(path) for path in REQUIRED if not path.exists()]
    if missing:
        raise SystemExit(
            "Missing Navigation Engine V1 files:\n- "
            + "\n- ".join(missing)
        )

    print("Navigation Engine V1 installation verified.")
    print("Next:")
    print(
        "py -m unittest "
        "tests.test_navigation_graph "
        "tests.test_navigation_state_tracker "
        "tests.test_navigator "
        "tests.test_navigation_validator "
        "tests.test_vision_state -v"
    )
    print("py -m examples.navigation_demo")


if __name__ == "__main__":
    main()
