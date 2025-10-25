from src.broadcasters.base_broadcaster import BaseBroadcaster
import numpy as np
from datetime import datetime
from uuid import uuid4
from src.services.auth_service import AuthService
import json
import asyncio


class OrderBroadcaster(BaseBroadcaster):
    def __init__(self, host, port, interval: float, price_lower_bound: float, price_upper_bound: float, ticker: str, auth_service: AuthService):
        super().__init__(host, port, interval)
        self.price_lower_bound = price_lower_bound
        self.price_upper_bound = price_upper_bound
        self.ticker = ticker
        self.auth_service = auth_service
        self.orders = []

    def create_message(self):
        return self.create_random_order()

    def create_random_order(self):
        order_type = np.random.choice(["Buy", "Sell"])

        price = np.round(np.random.uniform(
            self.price_lower_bound, self.price_upper_bound), 2)

        quantity = np.random.randint(1, 50)

        order = {
            'id': uuid4().hex,
            'type': order_type,
            'price': price,
            'quantity': quantity,
            'ticker': self.ticker,
            'user_id': 'trading.bot@colorado.edu',
            'timestamp': datetime.now().isoformat()
        }

        self.orders.append(order)

        return {'order': order, 'type': 'update'}

    async def initial_connection_action(self, client):
        await self.broadcast_batch(client)

    def create_batch_message(self):
        return {'orders': self.orders, 'type': 'batch'}

    async def on_message(self, msg, websocket):
        message_type = msg.get("type", None)

        if not message_type:
            # handle error more gracefully here
            return

        elif message_type == "order":
            token = msg.get("token", None)
            response = self.auth_service.validate_token(token)

            if response.get("success", False) == False:
                error_type, error_message = response.get(
                    "error_code", None), response.get("error_message", None)
                print(f"ERROR: {error_type}, {error_message}")
                await websocket.send(json.dumps({"type": "error", "error_type": error_type, "error_message": error_message}))
                return

            order = msg.get("order", None)

            if not order:
                print("NO ORDER")
                return

            else:
                price = order.get("price")
                if price <= 0:
                    await websocket.send(json.dumps({"type": "error", "error_type": "VALUE_ERROR", "error_message": "Price must be positive"}))
                    return
                user_id = response.get("user_id", None)
                order["user_id"] = user_id
                order['id'] = uuid4().hex
                order['ticker'] = 'QNTX'
                self.orders.append(order)
                print("PLACING ORDER")
                await asyncio.gather(
                    websocket.send(json.dumps(
                        {"type": "order_success", "message": "Order placed successfully"})),
                    self.broadcast_message({"type": "update", "order": order})
                )
        else:
            # implement logic for other message types
            pass
