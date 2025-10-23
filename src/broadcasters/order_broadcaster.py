from src.broadcasters.base_broadcaster import BaseBroadcaster
import numpy as np
from datetime import datetime
from uuid import uuid4


class OrderBroadcaster(BaseBroadcaster):
    def __init__(self, host, port, interval, price_lower_bound, price_upper_bound, ticker, rbac_system=None):
        super().__init__(host, port, interval)
        self.price_lower_bound = price_lower_bound
        self.price_upper_bound = price_upper_bound
        self.ticker = ticker
        self.rbac_system = rbac_system
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
            order = message_type.get("order", None)
            if not order:
                # again handle error later
                return
            else:
                user_id = msg.get("user_id", None)
                # implement rbac and order validation
                # valid_order = self.rbac_system.validate_order(user_id, order)
                # if not valid_order:
                #     self.broadcast_message(
                #         {"type": "error", "message": "Unable to process order!"})
                # return

                self.orders.append(order)
                await self.broadcast_message({"type": "update", "order": order})
        else:
            # implement logic for other message types
            pass
