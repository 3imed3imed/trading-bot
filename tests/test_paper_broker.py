import unittest

from paper_broker import parse_account, public_status


class PaperBrokerTests(unittest.TestCase):
    def test_active_unblocked_funded_account_is_ready(self):
        account = parse_account({
            "id": "secret-account-id",
            "status": "ACTIVE",
            "currency": "USD",
            "cash": "100",
            "equity": "100",
            "buying_power": "200",
            "trading_blocked": False,
            "account_blocked": False,
            "pattern_day_trader": False,
        })
        self.assertTrue(account.ready)
        status = public_status(account)
        self.assertEqual(status["connection"], "PASS")
        self.assertEqual(status["orders_submitted"], 0)
        self.assertNotIn("account_id", status["account"])

    def test_blocked_account_is_not_ready(self):
        account = parse_account({
            "status": "ACTIVE",
            "buying_power": "200",
            "trading_blocked": True,
            "account_blocked": False,
        })
        self.assertFalse(account.ready)
        self.assertEqual(public_status(account)["connection"], "BLOCKED")

    def test_unfunded_account_is_not_ready(self):
        account = parse_account({
            "status": "ACTIVE",
            "buying_power": "0",
            "trading_blocked": False,
            "account_blocked": False,
        })
        self.assertFalse(account.ready)


if __name__ == "__main__":
    unittest.main()
