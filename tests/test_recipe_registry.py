import unittest

from knowledge.recipe_registry import RecipeRegistry


class TestRecipeRegistry(unittest.TestCase):
    def test_dependencies(self):
        registry = RecipeRegistry()
        registry.register(
            {
                "item_id": "finished_item",
                "name": "Finished Item",
                "tier": 2,
                "ingredients": [
                    {
                        "item_id": "component",
                        "quantity": 1
                    }
                ]
            }
        )

        dependencies = registry.dependencies("finished_item")

        self.assertEqual(len(dependencies), 1)
        self.assertEqual(dependencies[0]["item_id"], "component")


if __name__ == "__main__":
    unittest.main()
