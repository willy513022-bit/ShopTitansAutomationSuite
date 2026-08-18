import unittest

from knowledge.knowledge_base import GameKnowledgeBase


class TestKnowledgeBase(unittest.TestCase):
    def test_load_summary(self):
        knowledge = GameKnowledgeBase("data").load()
        summary = knowledge.summary()

        self.assertGreaterEqual(summary["events"], 6)
        self.assertEqual(summary["recipes"], 0)
        self.assertEqual(summary["templates"], 0)
        self.assertEqual(summary["clickmaps"], 2)


if __name__ == "__main__":
    unittest.main()
