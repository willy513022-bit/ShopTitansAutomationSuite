from __future__ import annotations

from dataclasses import dataclass

from planner.blueprint_candidate import (
    BlueprintCandidate,
)


@dataclass(frozen=True, slots=True)
class BlueprintPriorityResult:
    candidate: BlueprintCandidate
    rank: int

    @property
    def item_name(self) -> str:
        return self.candidate.item_name

    @property
    def estimated_stage_time_seconds(self) -> int:
        return (
            self.candidate
            .estimated_stage_time_seconds
        )


class BlueprintPriorityScorer:
    """
    Blueprint 收藏優先順序 v1。

    排序原則：

        1. estimated_stage_time_seconds 越短越優先
        2. tier 越低越優先
        3. remaining 越少越優先
        4. item_name 作 deterministic tie-break

    第一版故意不用人工分數，
    先讓策略可預測、可測試。
    """

    @staticmethod
    def sort_key(
        candidate: BlueprintCandidate,
    ) -> tuple[
        int,
        int,
        int,
        str,
    ]:
        if not isinstance(
            candidate,
            BlueprintCandidate,
        ):
            raise TypeError(
                "candidate must be BlueprintCandidate"
            )

        return (
            candidate.estimated_stage_time_seconds,
            candidate.tier,
            candidate.remaining,
            candidate.item_name.casefold(),
        )

    def rank(
        self,
        candidates: list[
            BlueprintCandidate
        ]
        | tuple[
            BlueprintCandidate,
            ...
        ],
    ) -> tuple[
        BlueprintPriorityResult,
        ...
    ]:
        ordered = sorted(
            candidates,
            key=self.sort_key,
        )

        return tuple(
            BlueprintPriorityResult(
                candidate=candidate,
                rank=index,
            )
            for index, candidate
            in enumerate(
                ordered,
                start=1,
            )
        )

    def select_best(
        self,
        candidates: list[
            BlueprintCandidate
        ]
        | tuple[
            BlueprintCandidate,
            ...
        ],
    ) -> BlueprintCandidate | None:
        ranked = self.rank(
            candidates
        )

        if not ranked:
            return None

        return ranked[0].candidate