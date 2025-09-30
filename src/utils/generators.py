import numpy as np
from datetime import datetime


def create_random_order(price_lower_bound, price_upper_bound, ticker):
    order_type = np.random.choice(["Buy", "Sell"])

    price = np.round(np.random.uniform(
        price_lower_bound, price_upper_bound), 2)

    quantity = np.random.randint(1, 50)

    return {
        'type': order_type,
        'price': price,
        'quantity': quantity,
        'ticker': ticker,
        'timestamp': datetime.now().isoformat()
    }
