from __future__ import annotations

from runtime.executor import RuntimeExecutor
from runtime.input_driver import InputDriver
from runtime.live_world_state_provider import LiveWorldStateProvider
from runtime.runtime_engine import RuntimeEngine
from runtime.runtime_loop import RuntimeLoop


def main() -> int:
    print("=" * 60)
    print(" Shop Titans Automation Suite")
    print("=" * 60)
    print("[Main] Starting live runtime")
    print("[Main] Press Ctrl+C to stop")
    print()

    # Provider 負責：
    # - 擷取 Shop Titans 畫面
    # - 偵測 Popup
    # - 建立 WorldState
    # - 更新動態點擊座標
    provider = LiveWorldStateProvider(
        window_title="Shop Titans",
    )

    # Executor 必須共用 Provider 的 TargetResolver，
    # 才能取得 Vision 即時更新的座標。
    executor = RuntimeExecutor(
        resolver=provider.target_resolver,
        driver=InputDriver(),
    )

    runtime_engine = RuntimeEngine(
        executor=executor,
    )

    runtime_loop = RuntimeLoop(
        runtime_engine=runtime_engine,
        world_state_provider=provider,
        tick_interval=0.50,
        error_interval=1.00,
    )

    runtime_loop.run_forever()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
