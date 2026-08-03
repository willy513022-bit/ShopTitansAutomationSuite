"""
Legacy compatibility module.

請改用 runtime.window_manager。
"""

from .window_manager import WindowBounds, WindowManager

__all__ = [
    "WindowBounds",
    "WindowManager",
]