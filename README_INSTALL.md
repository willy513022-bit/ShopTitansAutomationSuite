# Installation

Extract this ZIP directly into:

```text
C:\PythonProject\ShopTitansAutomationSuiteV2
```

Allow Windows to merge folders.

This patch is additive. It does not intentionally overwrite the existing
Player Brain, Production Foundation, Runtime, Recovery, or Vision modules.

Run:

```powershell
py install_navigation_engine_v1.py
```

Then run:

```powershell
py -m unittest tests.test_navigation_graph tests.test_navigation_state_tracker tests.test_navigator tests.test_navigation_validator tests.test_vision_state -v
```

Demo:

```powershell
py -m examples.navigation_demo
```

Expected result:

```text
Ran 14 tests

OK
```
