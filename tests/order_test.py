import unittest
from src.broadcasters.order_broadcaster import OrderBroadcaster


class TestBroadcaster(OrderBroadcaster):
    """
    To implement:
    This class will provide a testing interface for the OrderBroadcaster service.
    It will override methods that involve network calls and keep functions that are unit testable.
    Specifically, it will test methods such as adding orders, and order verification logic.
    """

    def __init__(self):
        pass


class TestOrderService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.broadcaster = TestBroadcaster()
        cls.broadcaster.start_server()
