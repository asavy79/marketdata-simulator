from src.broadcasters.base_broadcaster import BaseBroadcaster
import numpy as np
from datetime import datetime
from uuid import uuid4


class OrderBroadcaster(BaseBroadcaster):
    def __init__(self, host, port, interval, price_lower_bound, price_upper_bound, ticker):
        super().__init__(host, port, interval)
        self.price_lower_bound = price_lower_bound
        self.price_upper_bound = price_upper_bound
        self.ticker = ticker
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
            'timestamp': datetime.now().isoformat()
        }

        self.orders.append(order)

        return {'order': order, 'type': 'update'}

    async def initial_connection_action(self, client):
        await self.broadcast_batch(client)

    def create_batch_message(self):
        return {'orders': self.orders, 'type': 'batch'}
