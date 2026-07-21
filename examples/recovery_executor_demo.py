from recovery.recovery_executor import RecoveryExecutor
ex=RecoveryExecutor()
print(ex.execute({"action":"RECONNECT"}))
print(ex.execute({"action":"CLOSE_POPUP"}))
print(ex.execute(None))
