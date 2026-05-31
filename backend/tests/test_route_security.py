import os
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from auth import create_access_token
from main import SCANNERS, app


class RouteSecurityTests(unittest.TestCase):
    secret = "test-secret-longer-than-thirty-two-bytes"

    def setUp(self):
        self.client = TestClient(app)

    def test_private_routes_require_bearer_token(self):
        self.assertEqual(
            self.client.get("/api/accounts-or-groups?provider=aws").status_code, 401
        )
        self.assertEqual(self.client.get("/api/history").status_code, 401)
        self.assertEqual(
            self.client.post(
                "/api/analyze",
                json={"provider": "aws", "target_scope": "us-east-1"},
            ).status_code,
            401,
        )

    @patch.dict(os.environ, {"JWT_SECRET": secret}, clear=False)
    def test_scope_discovery_accepts_valid_bearer_token(self):
        scanner = Mock()
        scanner.list_scopes.return_value = [{"id": "us-east-1", "name": "us-east-1"}]
        token = create_access_token(uuid4(), "operator@example.com")

        with patch.dict(SCANNERS, {"aws": scanner}, clear=True):
            response = self.client.get(
                "/api/accounts-or-groups?provider=aws",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["scopes"][0]["id"], "us-east-1")


if __name__ == "__main__":
    unittest.main()
