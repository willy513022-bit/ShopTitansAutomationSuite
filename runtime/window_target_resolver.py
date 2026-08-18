from __future__ import annotations

from runtime.click_target import ClickTarget
from runtime.window_manager import WindowManager


class WindowTargetResolver:
    """
    Convert a client-relative ClickTarget into a Windows
    screen-absolute ClickTarget.

    Input:
        ClickTarget(
            x=700,
            y=1400,
            source="clickmap:878x1550",
        )

    The input coordinates are relative to the Shop Titans
    client area.

    Output:
        ClickTarget(
            x=<screen x>,
            y=<screen y>,
            source="window:clickmap:878x1550",
        )
    """

    def __init__(
        self,
        window_manager: WindowManager,
    ) -> None:
        if not isinstance(
            window_manager,
            WindowManager,
        ):
            raise TypeError(
                "window_manager must be WindowManager"
            )

        self.window_manager = window_manager

    def resolve(
        self,
        target: ClickTarget,
    ) -> ClickTarget:
        if not isinstance(
            target,
            ClickTarget,
        ):
            raise TypeError(
                "target must be ClickTarget"
            )

        bounds = (
            self.window_manager
            .get_client_bounds()
        )

        if target.x < 0:
            raise ValueError(
                "target x cannot be negative"
            )

        if target.y < 0:
            raise ValueError(
                "target y cannot be negative"
            )

        if target.x >= bounds.width:
            raise ValueError(
                "target x is outside client area"
            )

        if target.y >= bounds.height:
            raise ValueError(
                "target y is outside client area"
            )

        screen_x, screen_y = (
            self.window_manager
            .client_to_screen(
                target.x,
                target.y,
            )
        )

        source = (
            f"window:{target.source}"
            if target.source
            else "window"
        )

        return ClickTarget(
            x=screen_x,
            y=screen_y,
            name=target.name,
            confidence=target.confidence,
            source=source,
        )