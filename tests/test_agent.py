import tempfile
import unittest
from pathlib import Path

from agent import ShopTitansAgent, WorldState, ScreenState, production_tasks


class AgentTests(unittest.TestCase):
    def test_diamond_is_denied(self):
        state = WorldState(
            screen=ScreenState("SHOP", 0.99),
            queue_remaining=1,
            gold=3_000_000_000,
            energy=5000,
        )
        text = ShopTitansAgent(
            tempfile.mkdtemp()
        ).run_once(state, production_tasks())
        self.assertNotIn("選擇：Diamond Rush", text)

    def test_unknown_creates_report(self):
        with tempfile.TemporaryDirectory() as temp:
            state = WorldState(
                screen=ScreenState("POPUP", 0.20),
                previous_screen="SHOP",
                current_task="Collect Production",
            )
            result = ShopTitansAgent(temp).run_once(state, [])
            self.assertIn("安全停止", result)
            reports = list(Path(temp).glob("notebook/unknown_*/report.md"))
            self.assertEqual(len(reports), 1)


if __name__ == "__main__":
    unittest.main()
