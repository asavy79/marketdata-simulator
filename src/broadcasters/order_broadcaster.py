from src.broadcasters.base_broadcaster import BaseBroadcaster
import numpy as np
from datetime import datetime
from uuid import uuid4
from src.services.auth.auth_service import AuthService
import json
import asyncio
from typing import List
from websockets.asyncio.server import ServerConnection


class OrderBroadcaster(BaseBroadcaster):
    def __init__(self, host, port, interval: float, price_lower_bound: float, price_upper_bound: float, ticker: str, auth_service: AuthService, tickers: List[str]):
        super().__init__(host, port, interval)
        self.price_lower_bound = price_lower_bound
        self.price_upper_bound = price_upper_bound
        self.ticker = ticker
        self.auth_service = auth_service

        self.orders = []

        self.order_map = self.create_ticker_map(tickers)
        self.locks = {ticker: asyncio.Lock() for ticker in tickers}
        self.client_subscriptions = self.create_subscription_map(tickers)

        self.orders_lock = asyncio.Lock()

    def create_ticker_map(self, tickers: List[str]):
        ticker_map = {}
        for ticker in tickers:
            ticker_map[ticker] = {"bids": {}, "asks": {}}
        return ticker_map

    def create_subscription_map(self, tickers: List[str]):
        return {ticker: set() for ticker in tickers}

    async def create_message(self):
        order = await self.create_random_order()
        return order

    async def create_random_order(self):
        order_type = np.random.choice(["Buy", "Sell"])

        price = np.round(np.random.uniform(
            self.price_lower_bound, self.price_upper_bound), 2)

        quantity = np.random.randint(1, 50)

        ticker = "QNTX"

        order = {
            'id': uuid4().hex,
            'type': order_type,
            'price': price,
            'quantity': quantity,
            'ticker': ticker,
            'user_id': 'tradingbot@colorado.edu',
            'timestamp': datetime.now().isoformat()
        }

        async with self.orders_lock:
            self.orders.append(order)

        async with self.locks[ticker]:
            self.order_map

        return {'order': order, 'type': 'update'}

    async def initial_connection_action(self, client: ServerConnection):
        ticker = self.extract_ticker(client)
        if not ticker:
            await self.send_error(client, "ROOM_ERROR", "Ticker string not provided!")
        elif ticker not in self.client_subscriptions:
            await self.send_error(client, "INVALID_TICKER", f"Ticker: {ticker} is invalid")
        else:
            async with self.clients_lock:
                self.client_subscriptions[ticker].add(client)
            await self.broadcast_batch(client)

    def extract_ticker(self, client: ServerConnection):
        try:
            raw_url = client.request.path
            ticker = raw_url.split("/")[-1].upper()
            return ticker
        except Exception as e:
            print(e)
            return None

    async def create_batch_message(self):
        async with self.orders_lock:
            order_snapshot = self.orders.copy()
        return {'orders': order_snapshot, 'type': 'batch'}

    async def on_message(self, msg: dict, websocket: ServerConnection):
        message_type = msg.get("type", None)

        if not message_type:
            await self.send_error(websocket, "MISSING_TYPE", "A message type is required")
            return

        elif message_type == "order":
            await self.handle_order(websocket, msg)
        else:
            await self.send_error(websocket, "INVALID_MESSAGE_TYPE", "Message type is invalid")

    async def handle_order(self, websocket: ServerConnection, msg: dict):
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
            await self.send_error(websocket, "NO_ORDER", "Order field must be present")
            return

        else:
            price = order.get("price")
            if price <= 0:
                await websocket.send(json.dumps({"type": "error", "error_type": "VALUE_ERROR", "error_message": "Price must be positive"}))
                return
            user_id = response.get("user_id", None)

        ticker = "QNTX"
        order["user_id"] = user_id
        order['id'] = uuid4().hex
        order['ticker'] = ticker
        async with self.orders_lock:
            self.orders.append(order)

        side = "bids" if order["type"] == "Buy" else "asks"
        async with self.locks[ticker]:
            self.order_map[ticker][side][price] = self.order_map[ticker][side].get(
                price, 0) + order['quantity']
        await asyncio.gather(
            websocket.send(json.dumps(
                {"type": "order_success", "message": "Order placed successfully"})),
            self.broadcast_message({"type": "update", "order": order})
        )
