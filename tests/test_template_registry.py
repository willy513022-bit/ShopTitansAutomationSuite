import unittest
from pathlib import Path

from knowledge.template_registry import TemplateRegistry


class TestTemplateRegistry(unittest.TestCase):
    def test_register_and_resolve(self):
        registry = TemplateRegistry()
        registry.register(
            {
                "template_id": "collect_button",
                "screen_state": "GUILD_GIFT",
                "relative_path": "buttons/collect.png",
                "threshold": 0.9
            }
        )

        resolved = registry.resolve_path("collect_button", "data/templates")

        self.assertEqual(
            resolved,
            Path("data/templates/buttons/collect.png"),
        )


if __name__ == "__main__":
    unittest.main()
