import unittest
import json
from unittest.mock import patch

# Mock FastAPI TestClient
from fastapi.testclient import TestClient
from main import app

class TestJobAnalyzeIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        
    def test_a_postgres_transferable(self):
        # Missing skill + transferable evidence
        payload = {
            "job_description": "We need a backend developer with PostgreSQL experience.",
            "resume_data": {
                "projects": [
                    {
                        "name": "Database App",
                        "description": "Built applications using MySQL and complex SQL queries.",
                        "technologies": ["MySQL", "SQL"]
                    }
                ],
                "experience": [],
                "skills": ["Python", "MySQL"]
            }
        }
        
        response = self.client.post("/job/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify Rule-Based authority
        self.assertIn("PostgreSQL", data["match"]["missing_skills"])
        self.assertNotIn("PostgreSQL", data["match"]["matched_skills"])
        
        # Verify ML Evidence
        evidence = data.get("transferable_evidence", [])
        self.assertTrue(len(evidence) > 0)
        
        found_transferable = False
        for e in evidence:
            if e["skill"] == "PostgreSQL" and e["classification"] == "transferable":
                found_transferable = True
        self.assertTrue(found_transferable)

    def test_b_kubernetes_related(self):
        # Missing skill + related technology
        payload = {
            "job_description": "We need experience deploying to Kubernetes clusters.",
            "resume_data": {
                "projects": [
                    {
                        "name": "Container App",
                        "description": "Containerized applications using Docker.",
                        "technologies": ["Docker"]
                    }
                ],
                "experience": [],
                "skills": ["Docker"]
            }
        }
        
        response = self.client.post("/job/analyze", json=payload)
        data = response.json()
        
        # Verify Rule-Based authority
        self.assertIn("Kubernetes", data["match"]["missing_skills"])
        
        # Verify ML Evidence
        evidence = data.get("transferable_evidence", [])
        self.assertTrue(len(evidence) > 0)
        
        found_related = False
        for e in evidence:
            if e["skill"] == "Kubernetes" and e["classification"] == "related_but_not_equivalent":
                found_related = True
        self.assertTrue(found_related)

    def test_c_irrelevant_project(self):
        # Missing skill + irrelevant project
        payload = {
            "job_description": "We need a backend developer with PostgreSQL experience.",
            "resume_data": {
                "projects": [
                    {
                        "name": "Design App",
                        "description": "Designed logos and branding materials.",
                        "technologies": ["Illustrator"]
                    }
                ],
                "experience": [],
                "skills": ["Design"]
            }
        }
        
        response = self.client.post("/job/analyze", json=payload)
        data = response.json()
        
        # Verify Rule-Based authority
        self.assertIn("PostgreSQL", data["match"]["missing_skills"])
        
        # Verify ML Evidence
        evidence = data.get("transferable_evidence", [])
        # Should be empty since it's classified as not_relevant
        self.assertEqual(len(evidence), 0)

    def test_d_explicit_matched_skill(self):
        # Python is already matched, ML must NOT analyze it
        payload = {
            "job_description": "We need a Python developer.",
            "resume_data": {
                "projects": [
                    {
                        "name": "Script",
                        "description": "Wrote some scripts.",
                        "technologies": ["Bash"]
                    }
                ],
                "experience": [],
                "skills": ["Python"] # Explicit match
            }
        }
        
        response = self.client.post("/job/analyze", json=payload)
        data = response.json()
        
        self.assertIn("Python", data["match"]["matched_skills"])
        self.assertNotIn("Python", data["match"]["missing_skills"])
        
        evidence = data.get("transferable_evidence", [])
        # Since Python is matched, and no other missing skill has transferable evidence, it should be empty
        self.assertEqual(len(evidence), 0)

    @patch('ml.job_transferable_evidence.find_transferable_evidence')
    def test_e_ml_failure_graceful_fallback(self, mock_find):
        # Simulate ML failure
        mock_find.side_effect = Exception("Simulated ML Crash")
        
        payload = {
            "job_description": "We need a Python developer with PostgreSQL.",
            "resume_data": {
                "projects": [],
                "experience": [],
                "skills": ["Python"]
            }
        }
        
        response = self.client.post("/job/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Output must be completely normal rule-based match
        self.assertIn("Python", data["match"]["matched_skills"])
        self.assertIn("PostgreSQL", data["match"]["missing_skills"])
        
        # ML failed, so evidence is empty
        self.assertEqual(data.get("transferable_evidence"), [])

if __name__ == '__main__':
    unittest.main()
