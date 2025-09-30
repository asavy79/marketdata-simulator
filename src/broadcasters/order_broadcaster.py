from src.broadcasters.base_broadcaster import BaseBroadcaster
import numpy as np
from datetime import datetime


class OrderBroadcaster(BaseBroadcaster):
    def __init__(self, host, port, interval, price_lower_bound, price_upper_bound, ticker):
        super().__init__(host, port, interval)
        self.price_lower_bound = price_lower_bound
        self.price_upper_bound = price_upper_bound
        self.ticker = ticker

    def create_message(self):
        return self.create_random_order()

    def create_random_order(self):
        order_type = np.random.choice(["Buy", "Sell"])

        price = np.round(np.random.uniform(
            self.price_lower_bound, self.price_upper_bound), 2)

        quantity = np.random.randint(1, 50)

        return {
            'type': order_type,
            'price': price,
            'quantity': quantity,
            'ticker': self.ticker,
            'timestamp': datetime.now().isoformat()
        }
