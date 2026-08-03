from __future__ import annotations

import ctypes
import sys
from pathlib import Path

# 統一多螢幕與 Windows DPI 的實體座標。
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except (AttributeError, OSError):
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass

import pygetwindow as gw

# 讓 examples 可以直接 import 專案
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vision.capture import screenshot
from runtime.runtime_engine import RuntimeEngine
from runtime.executor import RuntimeExecutor
from runtime.input_driver import InputDriver
from runtime.target_resolver import TargetResolver
from runtime.target_updater import TargetUpdater

from vision.popup_detector import PopupDetector
from vision.popup_parser import PopupParser

from vision.vision_engine import VisionEngine

from world_state.world_state_builder import WorldStateBuilder
from vision.popup_models import PopupType

POPUP_ASSET_DIRECTORIES = {
    PopupType.RECONNECT: (
        PROJECT_ROOT / "assets" / "popups" / "reconnect"
    ),
    PopupType.PAID_OFFER: (
        PROJECT_ROOT / "assets" / "popups" / "paid_offer"
    ),
    PopupType.UPGRADE_FINISHED: (
        PROJECT_ROOT / "assets" / "popups" / "upgrade_finished"
    ),
}

def register_popup_templates(
    detector: PopupDetector,
) -> int:
    """載入 assets/popups 裡的所有 PNG 模板。"""

    registered_count = 0

    for popup_type, directory in POPUP_ASSET_DIRECTORIES.items():
        if not directory.exists():
            print(f"[WARNING] 找不到模板資料夾：{directory}")
            continue

        for path in sorted(directory.glob("*.png")):
            detector.register_file(
                popup_type=popup_type,
                path=path,
                template_id=path.stem,
            )

            registered_count += 1

            print(
                f"    loaded {popup_type.value:<18} "
                f"{path.name}"
            )

    return registered_count

def popup_center_to_screen(
    *,
    popup,
    frame,
    window_title: str,
) -> tuple[int, int]:
    """將 PopupDetector 的影像座標轉成 Windows 螢幕座標。"""

    if popup.location is None or popup.size is None:
        raise ValueError("Popup detection has no location or size")

    windows = gw.getWindowsWithTitle(window_title)

    valid_windows = [
        window
        for window in windows
        if window.width > 0
        and window.height > 0
        and not window.isMinimized
    ]

    if not valid_windows:
        raise RuntimeError(
            f"Unable to find active window: {window_title!r}"
        )

    window = valid_windows[0]

    left, top = popup.location
    width, height = popup.size

    image_center_x = left + width / 2
    image_center_y = top + height / 2

    frame_height, frame_width = frame.shape[:2]

    scale_x = frame_width / window.width
    scale_y = frame_height / window.height

    relative_x = round(image_center_x / scale_x)
    relative_y = round(image_center_y / scale_y)

    screen_x = window.left + relative_x
    screen_y = window.top + relative_y

    print()
    print("[Target coordinates]")
    print(f"    template        = {popup.template_id}")
    print(f"    image center    = ({image_center_x:.1f}, {image_center_y:.1f})")
    print(f"    window origin   = ({window.left}, {window.top})")
    print(f"    scale           = ({scale_x:.4f}, {scale_y:.4f})")
    print(f"    screen position = ({screen_x}, {screen_y})")

    return screen_x, screen_y

def main() -> int:

    print("=" * 60)
    print(" Shop Titans Runtime Pipeline Demo")
    print("=" * 60)

    #
    # Capture
    #

    frame = screenshot("Shop Titans")

    if frame is None:
        print("[ERROR] 無法擷取 Shop Titans 視窗")
        return 1

    print("[1] Capture")
    print(f"    frame shape = {frame.shape}")

    #
    # Vision
    #

    vision = VisionEngine()

    vision_result = vision.analyze(frame)

    print("[2] Vision")

    print(
        f"    screen = {vision_result.screen_state.name}"
    )

    #
    # Popup
    #

    popup_detector = PopupDetector()

    print("[3] Popup templates")

    template_count = register_popup_templates(
        popup_detector,
    )

    print(f"    total = {template_count}")

    popup = popup_detector.detect_best(frame)

    popup_state = None

    if popup is None:

        print("[3] Popup")

        print("    no popup")

    else:

        popup_state = PopupParser().parse(popup)

        print("[3] Popup")

        print(
            f"    {popup.popup_type.value}"
        )

    #
    # WorldState
    #

    builder = WorldStateBuilder()

    world = builder.build(
        vision_result=vision_result,
        popup_state=popup_state,
    )

    print("[4] WorldState")

    print(
        f"    screen = {world.screen}"
    )

    print(
        f"    popup = {world.popup}"
    )

    #
    # Runtime
    #

    resolver = TargetResolver()

    if popup is not None and popup_state is not None:
        popup_action = PopupParser().action_for(popup_state)

        # 目前只有 reconnect_button 經過真機驗證。
        # 其他 Popup 仍需準備可點擊按鈕的小模板。
        if (
            popup_action.target_name == "reconnect_button"
            and popup.template_id == "reconnect_button"
        ):
            screen_x, screen_y = popup_center_to_screen(
                popup=popup,
                frame=frame,
                window_title="Shop Titans",
            )

            updater = TargetUpdater(resolver)

            target = updater.update_popup_target(
                detection=popup,
                target_name=popup_action.target_name,
                screen_x=screen_x,
                screen_y=screen_y,
            )

            print()
            print("[TargetUpdater]")
            print(f"    registered = {target}")
        else:
            print()
            print(
                "[WARNING] Popup was detected, but its clickable "
                "button template is not ready."
            )
            print(f"    target_name = {popup_action.target_name}")
            print(f"    template    = {popup.template_id}")
            return 0

    executor = RuntimeExecutor(
        resolver=resolver,
        driver=InputDriver(),
    )

    runtime = RuntimeEngine(
        executor=executor,
    )

    print("[5] Runtime")

    runtime.tick(world)

    print()
    print("Pipeline finished.")
    print("=" * 60)

    return 0
    executor = RuntimeExecutor(
        resolver=resolver,
        driver=InputDriver(),
    )

    runtime = RuntimeEngine(
        executor=executor,
    )

    print("[5] Runtime")

    runtime.tick(world)
    print()

    print("Pipeline finished.")

    print("=" * 60)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())