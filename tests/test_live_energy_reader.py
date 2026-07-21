from detectors.energy_detector import (
    EnergyDetector,
)


def main() -> None:
    print("Live Energy Reader 測試")
    print("=" * 70)

    try:
        result = EnergyDetector().detect(
            save_debug=True
        )

    except Exception as error:
        print("偵測失敗：", error)
        return

    value = result.recognized

    print("raw_text：", repr(value.raw_text))
    print("confidence：", value.confidence)
    print("current：", value.current)
    print("maximum：", value.maximum)
    print("valid：", value.valid)
    print(
        "debug：",
        result.debug_image_path,
    )


if __name__ == "__main__":
    main()
