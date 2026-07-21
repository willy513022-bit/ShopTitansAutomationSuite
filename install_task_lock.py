from pathlib import Path


EXPORT_BLOCK = '''\nfrom .task_lock import (\n    TaskLockManager,\n    TaskLockSnapshot,\n    TaskLockError,\n    TaskLockAlreadyActiveError,\n    TaskLockOwnershipError,\n)\n'''


def main() -> None:
    project_root = Path(__file__).resolve().parent
    init_file = project_root / "core" / "__init__.py"
    task_lock_file = project_root / "core" / "task_lock.py"

    if not task_lock_file.exists():
        raise SystemExit("找不到 core/task_lock.py，請先把 ZIP 解壓縮到專案根目錄。")
    if not init_file.exists():
        raise SystemExit("找不到 core/__init__.py。")

    content = init_file.read_text(encoding="utf-8")
    if "from .task_lock import" not in content:
        init_file.write_text(content.rstrip() + "\n" + EXPORT_BLOCK, encoding="utf-8")
        print("已更新 core/__init__.py")
    else:
        print("core/__init__.py 已包含 TaskLock exports，略過。")

    print("TaskLockManager 安裝完成。")


if __name__ == "__main__":
    main()
