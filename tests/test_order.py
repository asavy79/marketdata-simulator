import unittest
from src.broadcasters.order_broadcaster import OrderBroadcaster
import json
from src.services.auth.auth_service import AuthService
from typing import List


class TestAuthService(AuthService):

    def __init__(self):
        pass

    def validate_token(self, token):
        if token:
            return {"success": True, "user_id": "dummy_uid"}
        else:
            return {"success": False, "error_message": "Token verification failed", "error_code": "TEST_ERROR"}

    def validate_user_order(self, user_id, order_amount, side):
        return True


class TestSocket():

    def __init__(self):
        self.received_messages = []

    async def send(self, message):
        self.received_messages.append(message)

    def contains_message(self, message):
        return message in self.received_messages

    def has_messages(self):
        return len(self.received_messages) > 0

    def get_messages(self):
        return self.received_messages


class TestBroadcaster(OrderBroadcaster):
    """
    To implement:
    This class will provide a testing interface for the OrderBroadcaster service.
    It will override methods that involve network calls and keep functions that are unit testable.
    Specifically, it will test methods such as adding orders, and order verification logic.
    """

    def __init__(self, host, port, interval: float, price_lower_bound: float, price_upper_bound: float, ticker: str, auth_service: AuthService, tickers: List[str]):
        super().__init__(host, port, interval, price_lower_bound,
                         price_upper_bound, ticker, auth_service, tickers)
        self.received_messages = []

    def add_connection(self, connection: TestSocket, ticker):
        self.clients.add(connection)

    def start_server(self):
        return


class TestOrderService(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):

        cls.auth_service = TestAuthService()
        cls.broadcaster = TestBroadcaster(host="localhost", port=8765, interval=30, price_lower_bound=10,
                                          price_upper_bound=20, ticker="QNTX", auth_service=cls.auth_service, tickers=["QNTX"])
        cls.broadcaster.start_server()

    async def test_order_without_token(self):

        socket_1 = TestSocket()

        order_payload = {
            "order": {},
            "token": None
        }

        await self.broadcaster.handle_order(socket_1, order_payload)

        self.assertTrue(socket_1.has_messages())

        messages = socket_1.get_messages()
        response_message = json.loads(messages[0])
        print(response_message)

        self.assertTrue(response_message["error_type"] == "TEST_ERROR")
