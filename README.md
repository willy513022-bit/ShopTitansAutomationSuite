# ShopTitansAutomationSuite V2 — First Code

第一份可執行的 Autonomous Agent 骨架。

包含：
- WorldState
- Rule Engine
- Decision Engine
- Safety Policy
- Black Box（最近 100 步）
- Unknown Notebook
- Explain Engine
- Production 任務範例
- 單元測試

執行：
```bash
python main.py
```

測試：
```bash
python -m unittest discover -s tests -v
```

這一版不會操作遊戲；它先建立 AI 的腦、記憶與安全機制。
