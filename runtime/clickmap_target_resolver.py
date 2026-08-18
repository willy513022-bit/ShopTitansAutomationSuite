from __future__ import annotations

from knowledge.clickmap_registry import ClickMapRegistry
from runtime.click_target import ClickTarget


class ClickMapTargetResolver:
    """
    Resolve a symbolic runtime target name into a ClickTarget
    using an already-loaded ClickMapRegistry.

    No mouse input is performed here.
    """

    def __init__(
        self,
        registry: ClickMapRegistry,
        resolution: str,
    ) -> None:
        if not isinstance(
            registry,
            ClickMapRegistry,
        ):
            raise TypeError(
                "registry must be ClickMapRegistry"
            )

        normalized_resolution = (
            str(resolution).strip()
        )

        if not normalized_resolution:
            raise ValueError(
                "resolution cannot be empty"
            )

        self.registry = registry
        self.resolution = (
            normalized_resolution
        )

    def resolve(
        self,
        target_name: str,
    ) -> ClickTarget:
        normalized_name = (
            str(target_name).strip()
        )

        if not normalized_name:
            raise ValueError(
                "target_name cannot be empty"
            )

        point = self.registry.get_point(
            self.resolution,
            normalized_name,
        )

        if point is None:
            raise KeyError(
                f"No clickmap point for "
                f"{normalized_name!r} at "
                f"{self.resolution!r}"
            )

        x, y = point

        return ClickTarget(
            x=x,
            y=y,
            name=normalized_name,
            confidence=1.0,
            source=(
                f"clickmap:{self.resolution}"
            ),
        )