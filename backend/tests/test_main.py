import unittest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

try:
    from fastapi import BackgroundTasks

    from ai_analyzer import CostAnalysis
    from main import AnalyzeRequest, SCANNERS, analyze, manager, run_analysis
except ModuleNotFoundError as exc:
    if exc.name not in {"asyncpg", "fastapi"}:
        raise
    BackgroundTasks = None


@unittest.skipIf(BackgroundTasks is None, "fastapi and asyncpg are not installed")
class AnalyzeRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_analyze_returns_background_job_details(self):
        tasks = BackgroundTasks()

        result = await analyze(
            AnalyzeRequest(provider="aws", target_scope="us-east-1"),
            tasks,
            uuid4(),
        )

        self.assertEqual(result["status"], "accepted")
        self.assertIn(str(result["analysis_id"]), result["websocket_url"])
        self.assertEqual(len(tasks.tasks), 1)

    async def test_background_analysis_broadcasts_and_persists_result(self):
        scanner = Mock()
        scanner.scan_resources.return_value = [{"provider": "aws", "id": "vol-1"}]
        expected = CostAnalysis(
            summary="One storage optimization found.",
            total_estimated_monthly_savings=12.5,
            issues=[
                {
                    "resource_id": "vol-1",
                    "resource_name": "vol-1",
                    "issue_type": "Unused Storage",
                    "severity": "Medium",
                    "description": "The volume is unattached.",
                    "estimated_savings": 12.5,
                    "fix_command": "aws ec2 delete-volume --volume-id vol-1",
                }
            ],
        )
        analyzer = Mock()
        analyzer.analyze.return_value = expected
        analysis_id = uuid4()
        user_id = uuid4()

        with (
            patch.dict(SCANNERS, {"aws": scanner}, clear=True),
            patch("main.AIAnalyzer", return_value=analyzer),
            patch("main.db.save_completed_analysis", new_callable=AsyncMock) as save,
            patch.object(manager, "broadcast", new_callable=AsyncMock) as broadcast,
        ):
            await run_analysis(
                analysis_id,
                user_id,
                AnalyzeRequest(provider="aws", target_scope="us-east-1"),
            )

        scanner.scan_resources.assert_called_once_with("us-east-1")
        save.assert_awaited_once()
        self.assertEqual(
            [call.args[1]["progress"] for call in broadcast.await_args_list],
            [5, 20, 45, 60, 85, 100],
        )
        self.assertEqual(broadcast.await_args_list[-1].args[1]["status"], "completed")
        self.assertEqual(broadcast.await_args_list[-1].args[1]["progress"], 100)


if __name__ == "__main__":
    unittest.main()
