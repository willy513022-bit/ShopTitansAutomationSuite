# Sprint 2 — Commit 1 installation

Copy the following folders into the project root and allow them to merge:

```text
core/
tests/
examples/
docs/
```

Add these exports to the end of `core/__init__.py` (the included installer
script can do this automatically):

```python
from .task_lock import (
    TaskLockManager,
    TaskLockSnapshot,
    TaskLockError,
    TaskLockAlreadyActiveError,
    TaskLockOwnershipError,
)
```

Then run:

```powershell
py install_task_lock.py
py -m unittest tests.test_task_lock -v
py -m examples.task_lock_demo
```

To rerun all currently available tests:

```powershell
py -m unittest discover -s tests -v
```
