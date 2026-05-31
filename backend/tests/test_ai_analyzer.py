import os
import unittest
from unittest.mock import Mock, patch

from ai_analyzer import AIAnalysisError, AIAnalyzer, CostAnalysis


class AIAnalyzerTests(unittest.TestCase):
    def test_analyze_returns_structured_payload(self):
        client = Mock()
        client.models.generate_content.return_value.text = """
        {
          "summary": "One unattached disk can be removed.",
          "total_estimated_monthly_savings": 12.5,
          "issues": [{
            "resource_id": "disk-1",
            "resource_name": "disk-1",
            "issue_type": "Unused Storage",
            "severity": "Medium",
            "description": "The disk is unattached.",
            "estimated_savings": 12.5,
            "fix_command": "gcloud compute disks delete disk-1 --zone=us-central1-a"
          }]
        }
        """

        analysis = AIAnalyzer("gcp", [], client=client).analyze()

        self.assertEqual(analysis.total_estimated_monthly_savings, 12.5)
        _, kwargs = client.models.generate_content.call_args
        self.assertEqual(kwargs["config"].response_schema, CostAnalysis)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_has_readable_error(self):
        with self.assertRaisesRegex(AIAnalysisError, "GEMINI_API_KEY"):
            AIAnalyzer("aws", [])


if __name__ == "__main__":
    unittest.main()
