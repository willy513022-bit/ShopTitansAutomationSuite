from __future__ import annotations

from dataclasses import dataclass

from recovery.reconnect_state import ConnectionState
from recovery.transaction import (
    ActionTransaction,
    TransactionState,
)


@dataclass(frozen=True)
class RecoveryDecision:
    should_pause: bool
    should_rebuild_world_state: bool
    should_retry_transaction: bool
    reason: str


class RecoveryManager:
    def evaluate(
        self,
        connection_state: ConnectionState,
        transaction: ActionTransaction | None,
        expected_effect_present: bool | None = None,
    ) -> RecoveryDecision:
        if connection_state in {
            ConnectionState.CONNECTION_LOST,
            ConnectionState.RECONNECT_AVAILABLE,
            ConnectionState.RECONNECTING,
            ConnectionState.LOADING,
        }:
            return RecoveryDecision(
                should_pause=True,
                should_rebuild_world_state=False,
                should_retry_transaction=False,
                reason="連線尚未恢復，暫停所有一般操作",
            )

        if connection_state in {
            ConnectionState.RECOVERING_STATE,
            ConnectionState.READY,
        }:
            if transaction is None:
                return RecoveryDecision(
                    should_pause=False,
                    should_rebuild_world_state=True,
                    should_retry_transaction=False,
                    reason="重新連線後重建 WorldState",
                )

            if transaction.state != TransactionState.AWAITING_CONFIRMATION:
                return RecoveryDecision(
                    should_pause=False,
                    should_rebuild_world_state=True,
                    should_retry_transaction=False,
                    reason="交易不在待確認狀態，僅重建 WorldState",
                )

            if expected_effect_present is True:
                transaction.commit()
                return RecoveryDecision(
                    should_pause=False,
                    should_rebuild_world_state=True,
                    should_retry_transaction=False,
                    reason="重新連線後確認效果仍存在，交易已提交",
                )

            if expected_effect_present is False:
                transaction.rollback("重新連線後確認事件被回溯")
                transaction.mark_retryable("事件回溯，重新加入待辦")
                return RecoveryDecision(
                    should_pause=False,
                    should_rebuild_world_state=True,
                    should_retry_transaction=(
                        transaction.state
                        == TransactionState.RETRYABLE
                    ),
                    reason="事件已回溯，重新排入任務",
                )

        return RecoveryDecision(
            should_pause=True,
            should_rebuild_world_state=False,
            should_retry_transaction=False,
            reason="連線狀態不明，採保守暫停",
        )
