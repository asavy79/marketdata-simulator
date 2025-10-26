from src.broadcasters.base_broadcaster import BaseBroadcaster
import numpy as np
from datetime import datetime
from uuid import uuid4
from src.services.auth.auth_service import AuthService
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

        self.orders_lock = asyncio.Lock()

    async def create_message(self):
        order = await self.create_random_order()
        return order

    async def create_random_order(self):
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

        async with self.orders_lock:
            self.orders.append(order)

        return {'order': order, 'type': 'update'}

    async def initial_connection_action(self, client):
        await self.broadcast_batch(client)

    async def create_batch_message(self):
        async with self.orders_lock:
            order_snapshot = self.orders.copy()
        return {'orders': order_snapshot, 'type': 'batch'}

    def validate_order(self, msg):
        token = msg.get("token", None)
        response = self.auth_service.validate_token(token)

        error_type, error_message = None, None

        if response.get("success", False) == False:
            error_type, error_message = response.get(
                "error_code", None), response.get("error_message", None)
            response = {"type": "error", "error_type": error_type,
                        "error_message": error_message}
        elif not msg.get("order", None):
            error_type, error_message = "INVALID_ORDER", "Must place a full order"
        else:
            user_id = response.get("user_id")
            order = msg.get("order")
            price = order.get("price")
            if price <= 0:
                error_type, error_message = "INVALID_ORDER", "Order price must be greater than 0"
            elif not self.auth_service.validate_user_order(user_id, price, order.get("type")):
                error_type, error_message = "INVALID_ORDER", "User is not able to place this order"

        return error_type, error_message

    async def send_error(self, websocket, error_type: str, error_message: str):
        """Centralized error response sender"""
        error_response = {
            "type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(error_response))

    async def on_message(self, msg, websocket):
        message_type = msg.get("type", None)

        if not message_type:
            await self.send_error(websocket, "MISSING_TYPE", "A message type is required")
            return

        elif message_type == "order":
            await self.handle_order(websocket, msg)
        else:
            pass

    async def handle_order(self, websocket, msg):
        token = msg.get("token", None)
        response = self.auth_service.validate_token(token)

        if response.get("success", False) == False:
            error_type, error_message = response.get(
                "error_code", None), response.get("error_message", None)
            print(f"ERROR: {error_type}, {error_message}")
            await self.send_error(websocket, error_type, error_message)
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
        async with self.orders_lock:
            self.orders.append(order)
        print("PLACING ORDER")
        await asyncio.gather(
            websocket.send(json.dumps(
                {"type": "order_success", "message": "Order placed successfully"})),
            self.broadcast_message({"type": "update", "order": order})
        )
