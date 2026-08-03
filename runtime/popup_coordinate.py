from __future__ import annotations

import ctypes

import numpy as np

# 必須在匯入 pygetwindow 前設定 DPI Awareness，
# 讓視窗座標、擷取影像和滑鼠使用一致的實體像素座標。
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except (AttributeError, OSError):
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass

import pygetwindow as gw

from vision.popup_models import PopupDetection


def popup_center_to_screen(
    *,
    popup: PopupDetection,
    frame: np.ndarray,
    window_title: str = "Shop Titans",
) -> tuple[int, int]:
    """
    將 PopupDetection 在擷取影像內的中心座標，
    轉換成 Windows 桌面的絕對螢幕座標。
    """

    if not isinstance(popup, PopupDetection):
        raise TypeError("popup must be PopupDetection")

    if not isinstance(frame, np.ndarray) or frame.size == 0:
        raise ValueError("frame must be a non-empty numpy array")

    title = window_title.strip()
    if not title:
        raise ValueError("window_title is required")

    if popup.location is None or popup.size is None:
        raise ValueError(
            "Popup detection must contain location and size"
        )

    windows = gw.getWindowsWithTitle(title)

    valid_windows = [
        window
        for window in windows
        if (
            window.width > 0
            and window.height > 0
            and not window.isMinimized
        )
    ]

    if not valid_windows:
        raise RuntimeError(
            f"Unable to find active window: {title!r}"
        )

    window = valid_windows[0]

    popup_left, popup_top = popup.location
    popup_width, popup_height = popup.size

    image_center_x = popup_left + popup_width / 2
    image_center_y = popup_top + popup_height / 2

    frame_height, frame_width = frame.shape[:2]

    scale_x = frame_width / window.width
    scale_y = frame_height / window.height

    if scale_x <= 0 or scale_y <= 0:
        raise RuntimeError("Invalid window-to-frame scale")

    relative_x = round(image_center_x / scale_x)
    relative_y = round(image_center_y / scale_y)

    screen_x = window.left + relative_x
    screen_y = window.top + relative_y

    return screen_x, screen_y