from __future__ import annotations

from ai.action import Action, ActionType
from planner.models import (
    AcquisitionMethod,
    CollectionPlan,
)


METHOD_TO_ACTION: dict[
    AcquisitionMethod,
    ActionType,
] = {
    AcquisitionMethod.CRAFT: (
        ActionType.START_CRAFT
    ),
    AcquisitionMethod.FUSION: (
        ActionType.START_FUSION
    ),
    AcquisitionMethod.QUEST: (
        ActionType.START_QUEST
    ),
    AcquisitionMethod.MARKET: (
        ActionType.BUY_MARKET
    ),
    AcquisitionMethod.DONATE: (
        ActionType.DONATE_COLLECTION
    ),
    AcquisitionMethod.WAIT: (
        ActionType.WAIT
    ),
    AcquisitionMethod.SKIP: (
        ActionType.WAIT
    ),
}


def collection_plan_to_action(
    plan: CollectionPlan,
) -> Action:
    step = plan.selected_step

    if step is None:
        return Action(
            action_type=ActionType.WAIT,
            score=0,
            reason=(
                "所有收藏任務目前皆無法推進"
            ),
            payload={
                "blocked_reasons": (
                    plan.blocked_reasons
                ),
            },
        )

    action_type = METHOD_TO_ACTION.get(
        step.method,
        ActionType.WAIT,
    )

    return Action(
        action_type=action_type,
        score=step.score,
        reason=step.reason,
        payload=step.payload,
    )
