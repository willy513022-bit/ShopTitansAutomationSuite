import tempfile
import unittest
from pathlib import Path

from knowledge.event_registry import EventRegistry
from knowledge.errors import KnowledgeValidationError
from knowledge.json_store import JsonStore


class TestEventRegistry(unittest.TestCase):
    def test_load_real_event_documents(self):
        registry = EventRegistry().load_directory("data/events")

        self.assertGreaterEqual(len(registry), 6)
        self.assertIsNotNone(registry.get("guild_gift"))
        self.assertTrue(registry.get("guild_gift")["interrupt"])

    def test_interrupt_events_are_sorted(self):
        registry = EventRegistry().load_directory("data/events")
        events = registry.interrupt_events()

        priorities = [event["priority"] for event in events]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_duplicate_event_rejected(self):
        registry = EventRegistry()
        document = {
            "event_id": "sample",
            "display_name": "Sample",
            "category": "interrupt",
            "priority": 1,
            "interrupt": True,
            "actions": [{"type": "COLLECT"}],
        }
        registry.register(document)

        with self.assertRaises(KnowledgeValidationError):
            registry.register(document)


if __name__ == "__main__":
    unittest.main()
