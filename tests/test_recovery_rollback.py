from recovery.reconnect_state import ConnectionState
from recovery.recovery_manager import RecoveryManager
from recovery.transaction import (
    ActionTransaction,
    TransactionState,
)


def main() -> None:
    print("Recovery Rollback 測試")
    print("=" * 72)

    transaction = ActionTransaction(
        transaction_id="tx-001",
        action_name="buy_market_item",
        expected_effects={
            "inventory_delta": 1,
            "gold_delta": -10000,
        },
    )

    transaction.mark_executing()
    transaction.mark_awaiting_confirmation()

    decision = RecoveryManager().evaluate(
        connection_state=ConnectionState.READY,
        transaction=transaction,
        expected_effect_present=False,
    )

    print("state：", transaction.state.value)
    print("retry：", decision.should_retry_transaction)
    print("reason：", decision.reason)

    assert transaction.state == TransactionState.RETRYABLE
    assert decision.should_retry_transaction is True

    print("測試通過")


if __name__ == "__main__":
    main()
