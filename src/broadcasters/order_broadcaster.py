from src.broadcasters.base_broadcaster import BaseBroadcaster
import numpy as np
import time
from src.utils.generators import create_random_order


class OrderBroadcaster(BaseBroadcaster):
    def __init__(self, host, port, interval, price_lower_bound, price_upper_bound, ticker):
        super().__init__(host, port, interval)
        self.price_lower_bound = price_lower_bound
        self.price_upper_bound = price_upper_bound
        self.ticker = ticker

    def create_message(self):
        return create_random_order(self.price_lower_bound, self.price_upper_bound, self.ticker)
