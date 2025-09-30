import unittest
import asyncio
from src.broadcasters.order_broadcaster import OrderBroadcaster
import websockets


class TestWebSocketServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.broadcaster = OrderBroadcaster(
            host="localhost",
            port=8765,
            interval=1,
            price_lower_bound=10,
            price_upper_bound=20,
            ticker="QNTX"
        )

        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        cls.server = cls.loop.run_until_complete(
            cls.broadcaster.start_server()
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.close()
        cls.loop.run_until_complete(cls.server.wait_closed())
        cls.loop.close()

    def test_connection(self):
        async def _test():
            async with websockets.connect('ws://localhost:8765') as ws:
                self.assertTrue(ws.open)
                print(
                    f"✓ Connected successfully. WebSocket state: {ws.state.name}")

        self.loop.run_until_complete(_test())


if __name__ == '__main__':
    unittest.main()
