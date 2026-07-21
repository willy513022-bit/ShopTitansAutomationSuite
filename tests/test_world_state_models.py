import unittest

from world_state import InventoryState, ProductionState, RecipeState


class WorldStateModelTests(unittest.TestCase):
    def test_inventory_state_copies_items(self):
        items = {"Wood Axe": 4}
        state = InventoryState(items)
        items["Wood Axe"] = 99
        self.assertEqual(4, state.quantity("Wood Axe"))

    def test_production_state_rejects_negative_slots(self):
        with self.assertRaises(ValueError):
            ProductionState(-1)

    def test_recipe_state_normalizes_materials(self):
        recipe = RecipeState("Wood Axe", 1, 70, {"Wood": 2})
        self.assertEqual(2, recipe.materials["Wood"])


if __name__ == "__main__":
    unittest.main()
