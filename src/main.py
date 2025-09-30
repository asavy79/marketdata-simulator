from src.broadcasters.order_broadcaster import OrderBroadcaster


if __name__ == "__main__":
    order_broadcaster = OrderBroadcaster(
        host="localhost", port=8765, interval=1, price_lower_bound=10, price_upper_bound=20, ticker="QNTX")

    order_broadcaster.start_server()
