import unittest

from evaluators import EvaluationResult


class EvaluationResultTests(unittest.TestCase):
    def test_copies_mutable_details(self):
        details = {"missing": 4}
        result = EvaluationResult("inventory", 8, "Missing stock", details=details)
        details["missing"] = 99
        self.assertEqual(4, result.details["missing"])

    def test_rejects_empty_evaluator(self):
        with self.assertRaises(ValueError):
            EvaluationResult(" ", 0, "reason")

    def test_score_factor_is_explainable(self):
        result = EvaluationResult("inventory", 8, "Missing stock", details={"missing": 4})
        factor = result.to_score_factor()
        self.assertEqual("inventory", factor["id"])
        self.assertEqual(8.0, factor["value"])
        self.assertEqual("Missing stock", factor["reason"])


if __name__ == "__main__":
    unittest.main()
