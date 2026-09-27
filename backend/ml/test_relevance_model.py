import unittest
from .relevance_model import load_relevance_model, calculate_relevance, RELEVANCE_THRESHOLD
from .relevance_api import analyze_relevance

class TestRelevanceModel(unittest.TestCase):
    
    def test_model_loads_successfully(self):
        # Ensure lazy loading works
        model = load_relevance_model()
        self.assertIsNotNone(model)
        
    def test_valid_inference(self):
        job = "Develop web applications using Django."
        res = "Built full-stack Python web applications utilizing Django and PostgreSQL."
        
        result = analyze_relevance(job, res)
        
        # Check structure
        self.assertIn("relevance_score", result)
        self.assertIn("is_relevant", result)
        self.assertIn("threshold", result)
        self.assertNotIn("candidate_has_skill", result) # Must not claim exact ownership
        self.assertNotIn("has_skill", result)
        
        # Check types
        self.assertIsInstance(result["relevance_score"], float)
        self.assertIsInstance(result["is_relevant"], bool)
        self.assertEqual(result["threshold"], RELEVANCE_THRESHOLD)
        
        # We know this should be highly relevant
        self.assertGreater(result["relevance_score"], 0.1)
        
        # Check logic application
        self.assertEqual(result["is_relevant"], result["relevance_score"] >= RELEVANCE_THRESHOLD)
        
    def test_empty_handling(self):
        # Empty job
        res1 = analyze_relevance("", "I have some skills.")
        self.assertFalse(res1["is_relevant"])
        self.assertEqual(res1["relevance_score"], 0.0)
        
        # Empty resume
        res2 = analyze_relevance("Must know Python.", "")
        self.assertFalse(res2["is_relevant"])
        self.assertEqual(res2["relevance_score"], 0.0)
        
        # Both empty
        res3 = analyze_relevance("", "")
        self.assertFalse(res3["is_relevant"])
        self.assertEqual(res3["relevance_score"], 0.0)

if __name__ == '__main__':
    unittest.main()
