from vision_core.calibration import ROICalibrator


def main() -> None:
    print("Energy ROI 校準")
    print("=" * 70)
    print(
        "請框選畫面上「目前能量 / 能量上限」"
        "的數字區域。"
    )
    print(
        "只框數字與斜線，"
        "不要包含太多背景或其他圖示。"
    )

    result = ROICalibrator().calibrate(
        "energy_value"
    )

    if not result.saved:
        print("已取消，沒有儲存")
        return

    print()
    print("已儲存 ROI")
    print("-" * 70)
    print("x：", result.roi.x)
    print("y：", result.roi.y)
    print("width：", result.roi.width)
    print("height：", result.roi.height)


if __name__ == "__main__":
    main()
