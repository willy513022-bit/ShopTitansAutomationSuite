from __future__ import annotations

from collections import defaultdict
from heapq import heappop, heappush
from typing import Dict, Iterable, List

from .screen import Screen
from .transition import Transition, TransitionAction


class ScreenGraph:
    def __init__(
        self,
        transitions: Iterable[Transition] | None = None,
    ) -> None:
        self._adjacency: Dict[
            Screen,
            List[Transition],
        ] = defaultdict(list)

        if transitions:
            for transition in transitions:
                self.add_transition(transition)

    def add_transition(
        self,
        transition: Transition,
    ) -> None:
        transition.validate()

        for existing in self._adjacency[
            transition.source
        ]:
            if (
                existing.target
                == transition.target
                and existing.action
                == transition.action
            ):
                return

        self._adjacency[
            transition.source
        ].append(transition)

    def transitions_from(
        self,
        screen: Screen,
    ) -> tuple[Transition, ...]:
        return tuple(
            self._adjacency.get(
                screen,
                (),
            )
        )

    def shortest_path(
        self,
        start: Screen,
        target: Screen,
    ) -> list[Transition]:
        if start == target:
            return []

        frontier: list[
            tuple[int, int, Screen]
        ] = []

        counter = 0

        heappush(
            frontier,
            (0, counter, start),
        )

        best_cost: Dict[
            Screen,
            int,
        ] = {
            start: 0
        }

        previous: Dict[
            Screen,
            tuple[Screen, Transition],
        ] = {}

        while frontier:
            cost, _, current = (
                heappop(frontier)
            )

            if current == target:
                break

            if cost != best_cost[current]:
                continue

            for transition in (
                self.transitions_from(current)
            ):
                next_cost = (
                    cost
                    + transition.cost
                )

                if next_cost < best_cost.get(
                    transition.target,
                    10**9,
                ):
                    best_cost[
                        transition.target
                    ] = next_cost

                    previous[
                        transition.target
                    ] = (
                        current,
                        transition,
                    )

                    counter += 1

                    heappush(
                        frontier,
                        (
                            next_cost,
                            counter,
                            transition.target,
                        ),
                    )

        if target not in previous:
            raise LookupError(
                "No navigation path: "
                f"{start.value} "
                f"-> {target.value}"
            )

        path: list[
            Transition
        ] = []

        cursor = target

        while cursor != start:
            source, transition = (
                previous[cursor]
            )

            path.append(
                transition
            )

            cursor = source

        path.reverse()

        return path


def build_default_screen_graph() -> ScreenGraph:
    graph = ScreenGraph()

    transitions = [
        # Shop -> Craft is a direct real UI action.
        Transition(
            Screen.SHOP,
            Screen.CRAFT,
            TransitionAction.OPEN_CRAFT,
        ),

        # Shop -> Fusion is also modeled as a direct
        # production entry point.
        Transition(
            Screen.SHOP,
            Screen.FUSION,
            TransitionAction.OPEN_FUSION,
        ),

        # Craft/Fusion can switch between each other
        # when the UI exposes those controls.
        Transition(
            Screen.CRAFT,
            Screen.FUSION,
            TransitionAction.SWITCH_TO_FUSION,
        ),
        Transition(
            Screen.FUSION,
            Screen.CRAFT,
            TransitionAction.SWITCH_TO_CRAFT,
        ),

        Transition(
            Screen.CRAFT,
            Screen.SHOP,
            TransitionAction.BACK,
        ),
        Transition(
            Screen.FUSION,
            Screen.SHOP,
            TransitionAction.BACK,
        ),

        Transition(
            Screen.SHOP,
            Screen.QUEST,
            TransitionAction.OPEN_QUEST,
        ),
        Transition(
            Screen.QUEST,
            Screen.SHOP,
            TransitionAction.BACK,
        ),

        Transition(
            Screen.SHOP,
            Screen.GUILD,
            TransitionAction.OPEN_GUILD,
        ),
        Transition(
            Screen.GUILD,
            Screen.SHOP,
            TransitionAction.BACK,
        ),

        Transition(
            Screen.SHOP,
            Screen.PET,
            TransitionAction.OPEN_PET,
        ),
        Transition(
            Screen.PET,
            Screen.SHOP,
            TransitionAction.BACK,
        ),

        Transition(
            Screen.SHOP,
            Screen.UPGRADE,
            TransitionAction.OPEN_UPGRADE,
        ),
        Transition(
            Screen.UPGRADE,
            Screen.SHOP,
            TransitionAction.BACK,
        ),

        Transition(
            Screen.SHOP,
            Screen.KING,
            TransitionAction.OPEN_KING,
        ),
        Transition(
            Screen.KING,
            Screen.SHOP,
            TransitionAction.BACK,
        ),

        Transition(
            Screen.MODAL,
            Screen.SHOP,
            TransitionAction.CLOSE_MODAL,
        ),
    ]

    for transition in transitions:
        graph.add_transition(
            transition
        )

    return graph