from recognizers.energy_recognizer import (
    EnergyRecognizer,
)


def main() -> None:
    print("Energy Recognizer Parser 測試")
    print("=" * 70)

    recognizer = EnergyRecognizer()

    cases = {
        "950 / 1000": (950, 1000),
        "80/1000": (80, 1000),
        "823 | 1000": (823, 1000),
        "O50 / 1OOO": (50, 1000),
    }

    for text, expected in cases.items():
        result = recognizer._parse(
            text
        )

        print(
            f"{text:<18} "
            f"→ {result.current} / "
            f"{result.maximum}"
        )

        assert (
            result.current,
            result.maximum,
        ) == expected

    print("測試通過")


if __name__ == "__main__":
    main()
