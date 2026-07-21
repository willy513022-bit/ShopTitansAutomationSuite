import unittest

from navigation import Screen
from vision import VisionState


class TestVisionState(unittest.TestCase):
    def test_valid_production_state(self):
        state = VisionState(
            screen=Screen.CRAFT,
            screen_confidence=0.97,
            production_mode="CRAFT",
            queue_remaining=7,
            completed_items=2,
            gold=3512120,
        )
        state.validate()
        self.assertEqual(state.queue_remaining, 7)

    def test_negative_queue_rejected(self):
        state = VisionState(
            screen=Screen.CRAFT,
            screen_confidence=0.97,
            queue_remaining=-1,
        )
        with self.assertRaises(ValueError):
            state.validate()
