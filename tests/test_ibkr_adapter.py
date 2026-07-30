import os
import unittest
from unittest.mock import patch

from ibkr_adapter import _gateway_url, parse_auth_status, public_status


class IbkrAdapterTests(unittest.TestCase):
    def test_ready_authenticated_paper_session(self):
        session = parse_auth_status(
            {"authenticated": True, "connected": True, "competing": False},
            [{"accountId": "DU123456"}],
        )
        self.assertTrue(session.ready)
        status = public_status(session)
        self.assertEqual(status["connection"], "PASS")
        self.assertEqual(status["account_count"], 1)
        self.assertEqual(status["orders_submitted"], 0)
        self.assertNotIn("DU123456", str(status))

    def test_competing_session_is_blocked(self):
        session = parse_auth_status(
            {"authenticated": True, "connected": True, "competing": True},
            [{"accountId": "DU123456"}],
        )
        self.assertFalse(session.ready)
        self.assertEqual(public_status(session)["connection"], "BLOCKED")

    def test_gateway_requires_https(self):
        with patch.dict(os.environ, {"IBKR_GATEWAY_URL": "http://gateway:5000/v1/api"}, clear=False):
            with self.assertRaises(RuntimeError):
                _gateway_url()


if __name__ == "__main__":
    unittest.main()
