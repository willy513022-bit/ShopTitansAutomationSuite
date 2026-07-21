import cv2
import mss
import numpy as np
import pygetwindow as gw

WINDOW_TITLE = "Shop Titans"

def screenshot(window_title: str = WINDOW_TITLE):
    windows = gw.getWindowsWithTitle(window_title)
    if not windows: return None
    window = windows[0]
    monitor = {"left":window.left,"top":window.top,"width":window.width,"height":window.height}
    if monitor["width"] <= 0 or monitor["height"] <= 0: return None
    with mss.mss() as sct:
        image = np.array(sct.grab(monitor))
    return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
