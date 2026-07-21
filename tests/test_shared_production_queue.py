import unittest

from core.account_capabilities import AccountCapabilities
from core.production import ProductionMode, QueueObservation, SharedProductionQueue


class TestSharedProductionQueue(unittest.TestCase):
    def test_shared_capacity_math(self):
        queue = SharedProductionQueue(
            AccountCapabilities(production_queue_capacity=10),
            QueueObservation(
                remaining_slots=5,
                ready_to_collect=2,
                mode=ProductionMode.CRAFT,
            ),
        )
        self.assertEqual(queue.occupied_slots, 5)
        self.assertTrue(queue.can_schedule(5))
        self.assertFalse(queue.can_schedule(6))
        self.assertTrue(queue.should_collect_first())
        self.assertEqual(queue.expected_remaining_after_collect(2), 7)

    def test_mode_switch_preserves_shared_slot_count(self):
        queue = SharedProductionQueue(
            AccountCapabilities(),
            QueueObservation(
                remaining_slots=3,
                ready_to_collect=0,
                mode=ProductionMode.CRAFT,
            ),
        )
        switched = queue.switch_mode(ProductionMode.FUSION)
        self.assertEqual(switched.mode, ProductionMode.FUSION)
        self.assertEqual(switched.remaining_slots, 3)

    def test_remaining_cannot_exceed_capacity(self):
        with self.assertRaises(ValueError):
            SharedProductionQueue(
                AccountCapabilities(production_queue_capacity=10),
                QueueObservation(
                    remaining_slots=11,
                    mode=ProductionMode.CRAFT,
                ),
            )
