from src.broadcasters.order_broadcaster import OrderBroadcaster
from src.services.auth.firebase_auth_service import FirebaseAuth

TICKERS = ["QNTX"]


if __name__ == "__main__":
    auth_service = FirebaseAuth()
    order_broadcaster = OrderBroadcaster(
        host="localhost", port=8765, interval=30, price_lower_bound=10, price_upper_bound=20, ticker="QNTX", auth_service=auth_service, tickers=TICKERS)

    order_broadcaster.start_server()
