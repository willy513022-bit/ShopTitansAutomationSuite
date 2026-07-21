from pathlib import Path
import json


REQUIRED = [
    Path("core/player_profile/profile.py"),
    Path("core/player_profile/collection_policy.py"),
    Path("core/player_profile/safety_policy.py"),
    Path("core/account_capabilities.py"),
    Path("core/production/shared_queue.py"),
    Path("data/player_profile/collector_v1.json"),
    Path("data/account_capabilities/default.json"),
    Path("data/game_rules/observations_v1.json"),
]


def main() -> None:
    missing = [str(path) for path in REQUIRED if not path.exists()]
    if missing:
        raise SystemExit("Missing installed files:\n- " + "\n- ".join(missing))

    with Path("data/player_profile/collector_v1.json").open(
        "r", encoding="utf-8"
    ) as file:
        profile = json.load(file)

    if not profile["collection"]["keep_legendary_forever"]:
        raise SystemExit("Collector safety verification failed.")

    print("Player Brain + Production Foundation installation verified.")
    print("Next:")
    print(
        "py -m unittest "
        "tests.test_player_profile "
        "tests.test_collection_policy "
        "tests.test_account_capabilities "
        "tests.test_shared_production_queue "
        "tests.test_safety_policy -v"
    )
    print("py -m examples.player_brain_production_demo")


if __name__ == "__main__":
    main()
