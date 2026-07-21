import unittest

from knowledge.clickmap_registry import ClickMapRegistry


class TestClickMapRegistry(unittest.TestCase):
    def test_load_empty_clickmap(self):
        registry = ClickMapRegistry()
        registry.load_file("data/clickmaps/example_1280x720.json")

        self.assertEqual(registry.resolutions(), ("1280x720",))
        self.assertIsNone(registry.get_point("1280x720", "collect"))


if __name__ == "__main__":
    unittest.main()
