import asyncio
import json
import random
import string
from datetime import datetime
from websockets.asyncio.client import connect


def random_id(prefix: str, length: int = 6):
    """Helper: generate something like 'BOT_ABC123'."""
    suffix = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}_{suffix}"


class DummyOrderClient:
    """
    Connects to your OrderBroadcaster websocket for a single ticker
    and sprays randomized limit orders ("Buy"/"Sell").
    """

    def __init__(
        self,
        ws_url: str,
        ticker: str,
        token: str,
        user_id: str,
        min_price: float = 95.0,
        max_price: float = 105.0,
        min_qty: int = 1,
        max_qty: int = 10,
        delay_between_orders: float = 0.5,
    ):
        """
        ws_url: full URL including ticker room, e.g. ws://localhost:8765/ws/MSFT
        ticker: symbol string, e.g. "MSFT"
        token: whatever your auth_service.validate_token() expects
        user_id: not directly sent in the order payload (server derives from token),
                 but useful if you want to label logs per-bot
        min_price/max_price: price range to sample
        min_qty/max_qty: order size range
        delay_between_orders: seconds to sleep between sends
        """
        self.ws_url = ws_url
        self.ticker = ticker
        self.token = token
        self.user_id = user_id
        self.min_price = min_price
        self.max_price = max_price
        self.min_qty = min_qty
        self.max_qty = max_qty
        self.delay_between_orders = delay_between_orders

        self.ws = None  # will hold the live websocket connection

    def _make_dummy_order(self) -> dict:
        """
        Build a single order payload that matches what handle_order() expects.
        Your server code expects:
            {
              "type": "order",
              "token": "...",
              "order": {
                  "price": <number>,
                  "quantity": <int>,
                  "ticker": "<TICKER>",
                  "type": "Buy" or "Sell"
              }
            }
        """
        side = random.choice(["Buy", "Sell"])
        price = round(random.uniform(self.min_price, self.max_price), 2)
        qty = random.randint(self.min_qty, self.max_qty)

        return {
            "type": "order",
            "token": self.token,
            "order": {
                "price": price,
                "quantity": qty,
                "ticker": self.ticker,
                "type": side,
            },
        }

    async def _sender_loop(self, num_orders: int | None = None):
        """
        Continuously send orders.
        num_orders:
            - if int, send exactly that many then stop
            - if None, run forever
        """
        sent = 0
        while num_orders is None or sent < num_orders:
            order_msg = self._make_dummy_order()
            await self.ws.send(json.dumps(order_msg))
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] [{self.user_id}] SENT -> {order_msg}")

            sent += 1
            await asyncio.sleep(self.delay_between_orders)

    async def _receiver_loop(self):
        """
        Listen for messages from server:
        - "order_success"
        - "update" (new top-of-book add)
        - "book_update" / "trade" (if you implemented live book updates)
        """
        try:
            async for raw in self.ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    msg = raw
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] [{self.user_id}] RECV <- {msg}")
        except Exception as e:
            print(f"[{self.user_id}] receiver_loop ended: {e}")

    async def run(self, num_orders: int | None = None):
        """
        Connect, then run sender + receiver concurrently.
        """
        async with connect(self.ws_url) as websocket:
            self.ws = websocket
            print(f"[{self.user_id}] connected to {self.ws_url}")

            # kick off sender and receiver tasks
            sender_task = asyncio.create_task(self._sender_loop(num_orders))
            recv_task = asyncio.create_task(self._receiver_loop())

            # wait until sender finishes (or forever if num_orders=None)
            await sender_task

            # after we're done sending, we can cancel receiver
            recv_task.cancel()
            # optional: swallow cancellation
            try:
                await recv_task
            except asyncio.CancelledError:
                pass

            print(f"[{self.user_id}] finished.")


async def main():
    """
    Example usage:
    - Spin up 3 dummy clients hitting the same ticker room.
    - Each one sends 20 random orders.
    """

    # Suppose your server exposes rooms like ws://localhost:8765/ws/<TICKER>
    TICKER = "QNTX"
    WS_URL = f"ws://localhost:8765/ws/{TICKER}"

    # Whatever your AuthService.validate_token() expects as "token"
    # If you're not validating yet, you can pass literally any string.
    token1 = "BOT_TOKEN"
    token2 = "BOT_TOKEN"
    token3 = "BOT_TOKEN"

    bot_a = DummyOrderClient(
        ws_url=WS_URL,
        ticker=TICKER,
        token=token1,
        user_id=random_id("A"),
        min_price=99.5,
        max_price=100.5,
        delay_between_orders=0.3,
    )

    bot_b = DummyOrderClient(
        ws_url=WS_URL,
        ticker=TICKER,
        token=token2,
        user_id=random_id("B"),
        min_price=100.0,
        max_price=101.0,
        delay_between_orders=0.4,
    )

    bot_c = DummyOrderClient(
        ws_url=WS_URL,
        ticker=TICKER,
        token=token3,
        user_id=random_id("C"),
        min_price=99.0,
        max_price=100.0,
        delay_between_orders=0.6,
    )

    # Run them all at once
    await asyncio.gather(
        bot_a.run(num_orders=20),
        bot_b.run(num_orders=20),
        bot_c.run(num_orders=20),
    )


if __name__ == "__main__":
    asyncio.run(main())
