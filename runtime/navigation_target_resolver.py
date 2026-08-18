from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from navigation import Transition, TransitionAction


DEFAULT_NAVIGATION_TARGETS = MappingProxyType(
    {
        TransitionAction.OPEN_PRODUCTION: "production_button",
        TransitionAction.SWITCH_TO_CRAFT: "craft_tab",
        TransitionAction.SWITCH_TO_FUSION: "fusion_tab",
        TransitionAction.BACK: "back_button",
        TransitionAction.OPEN_QUEST: "quest_button",
        TransitionAction.OPEN_GUILD: "guild_button",
        TransitionAction.OPEN_PET: "pet_button",
        TransitionAction.OPEN_UPGRADE: "upgrade_button",
        TransitionAction.OPEN_KING: "king_button",
        TransitionAction.CLOSE_MODAL: "close_modal_button",
    }
)


@dataclass(frozen=True, slots=True)
class NavigationTarget:
    action: TransitionAction
    target_name: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.action,
            TransitionAction,
        ):
            raise TypeError(
                "action must be TransitionAction"
            )

        target_name = self.target_name.strip()

        if not target_name:
            raise ValueError(
                "target_name cannot be empty"
            )

        object.__setattr__(
            self,
            "target_name",
            target_name,
        )


class NavigationTargetResolver:
    """
    Translate navigation actions into symbolic runtime targets.

    This layer intentionally contains no screen coordinates.

    Example:

        TransitionAction.OPEN_PRODUCTION
            -> "production_button"

    Runtime can later resolve the symbolic name into a ClickTarget
    using calibrated clickmaps, Vision, or template matching.
    """

    def __init__(
        self,
        targets: Mapping[
            TransitionAction,
            str,
        ]
        | None = None,
    ) -> None:
        source = (
            DEFAULT_NAVIGATION_TARGETS
            if targets is None
            else targets
        )

        normalized: dict[
            TransitionAction,
            str,
        ] = {}

        for action, target_name in source.items():
            if not isinstance(
                action,
                TransitionAction,
            ):
                raise TypeError(
                    "navigation target keys must be "
                    "TransitionAction"
                )

            normalized[action] = (
                NavigationTarget(
                    action=action,
                    target_name=str(
                        target_name
                    ),
                ).target_name
            )

        self._targets = MappingProxyType(
            normalized
        )

    def resolve_action(
        self,
        action: TransitionAction,
    ) -> NavigationTarget:
        if not isinstance(
            action,
            TransitionAction,
        ):
            raise TypeError(
                "action must be TransitionAction"
            )

        target_name = self._targets.get(
            action
        )

        if target_name is None:
            raise KeyError(
                f"No runtime target registered "
                f"for navigation action: "
                f"{action.value}"
            )

        return NavigationTarget(
            action=action,
            target_name=target_name,
        )

    def resolve_transition(
        self,
        transition: Transition,
    ) -> NavigationTarget:
        if not isinstance(
            transition,
            Transition,
        ):
            raise TypeError(
                "transition must be Transition"
            )

        return self.resolve_action(
            transition.action
        )

    def has_action(
        self,
        action: TransitionAction,
    ) -> bool:
        return action in self._targets