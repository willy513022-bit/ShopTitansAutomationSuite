import pytest
from runtime import DryRunRuntimeExecutor,RuntimeDecision,RuntimeDecisionKind
def test_dry_run_wait_never_executes_game_input():
 d=RuntimeDecision(RuntimeDecisionKind.WAIT,'idle');r=DryRunRuntimeExecutor().execute(d);assert r.decision is d and r.executed is False and 'without game input' in r.reason
def test_dry_run_rejects_unknown_object():
 with pytest.raises(TypeError): DryRunRuntimeExecutor().execute(object())
