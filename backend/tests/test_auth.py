import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

import jwt
from fastapi import HTTPException

from auth import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class AuthTests(unittest.TestCase):
    secret = "test-secret-longer-than-thirty-two-bytes"

    @patch.dict(os.environ, {"JWT_SECRET": secret}, clear=False)
    def test_token_round_trip_returns_user_id(self):
        user_id = uuid4()

        token = create_access_token(user_id, "operator@example.com")

        self.assertEqual(decode_access_token(token), user_id)

    @patch.dict(os.environ, {"JWT_SECRET": secret}, clear=False)
    def test_expired_token_is_rejected(self):
        token = jwt.encode(
            {
                "sub": str(uuid4()),
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
            self.secret,
            algorithm=ALGORITHM,
        )

        with self.assertRaises(HTTPException) as context:
            decode_access_token(token)

        self.assertEqual(context.exception.status_code, 401)

    @patch.dict(os.environ, {"JWT_SECRET": secret}, clear=False)
    def test_malformed_token_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            decode_access_token("not-a-valid-jwt")

        self.assertEqual(context.exception.status_code, 401)

    def test_password_hash_can_be_verified(self):
        password_hash = hash_password("correct-horse-battery-staple")

        self.assertTrue(verify_password("correct-horse-battery-staple", password_hash))
        self.assertFalse(verify_password("wrong-password", password_hash))


if __name__ == "__main__":
    unittest.main()
