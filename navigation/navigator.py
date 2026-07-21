from __future__ import annotations

from dataclasses import dataclass

from .graph import ScreenGraph
from .screen import Screen
from .state_tracker import NavigationStateTracker
from .transition import Transition


@dataclass(frozen=True)
class NavigationPlan:
    start: Screen
    target: Screen
    transitions: tuple[Transition, ...]

    @property
    def is_noop(self) -> bool:
        return not self.transitions

    @property
    def total_cost(self) -> int:
        return sum(transition.cost for transition in self.transitions)

    def screens(self) -> tuple[Screen, ...]:
        sequence = [self.start]
        sequence.extend(transition.target for transition in self.transitions)
        return tuple(sequence)


class Navigator:
    """Plans navigation paths.

    Runtime execution is intentionally injected later. This class does not
    click the game and does not assume that a transition succeeded.
    """

    def __init__(
        self,
        graph: ScreenGraph,
        tracker: NavigationStateTracker,
    ) -> None:
        self.graph = graph
        self.tracker = tracker

    def plan(
        self,
        target: Screen,
        *,
        minimum_confidence: float = 0.80,
    ) -> NavigationPlan:
        if not self.tracker.is_reliable(minimum_confidence):
            raise RuntimeError(
                "Current screen is unknown or confidence is too low. "
                "Vision must refresh the screen state before navigation."
            )

        start = self.tracker.current_screen
        transitions = tuple(self.graph.shortest_path(start, target))
        return NavigationPlan(
            start=start,
            target=target,
            transitions=transitions,
        )

    def replan_from_observation(
        self,
        *,
        observed_screen: Screen,
        confidence: float,
        target: Screen,
        minimum_confidence: float = 0.80,
    ) -> NavigationPlan:
        self.tracker.update(observed_screen, confidence)
        return self.plan(target, minimum_confidence=minimum_confidence)
