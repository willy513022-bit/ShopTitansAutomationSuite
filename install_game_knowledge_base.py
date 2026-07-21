from pathlib import Path
import sys


REQUIRED_PATHS = [
    Path("knowledge/knowledge_base.py"),
    Path("data/events/guild_gift.json"),
    Path("data/events/guild_energy.json"),
    Path("data/events/worker_offer.json"),
    Path("data/events/spin_ticket_bubble.json"),
    Path("data/events/daily_free_spin.json"),
    Path("data/events/king_caprice_extra_slot.json"),
]


def main() -> int:
    missing = [str(path) for path in REQUIRED_PATHS if not path.exists()]

    if missing:
        print("Game Knowledge Base installation check failed.")
        print("Missing files:")
        for path in missing:
            print(f"- {path}")
        print("Extract and merge the ZIP into the project root first.")
        return 1

    print("Game Knowledge Base V1 installation verified.")
    print("Next:")
    print(
        "py -m unittest tests.test_event_registry "
        "tests.test_recipe_registry tests.test_template_registry "
        "tests.test_clickmap_registry tests.test_knowledge_base -v"
    )
    print("py -m examples.knowledge_base_demo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
