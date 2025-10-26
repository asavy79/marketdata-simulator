# QuantX Order Simulator

A WebSocket-based order simulator with Firebase authentication, real-time order broadcasting, and orderbook management. This project is a part of the CUQuants QuantX platform, a system that helps educate members on market dynamics.

## Overview

The QuantX Order Simulator is a service that simulates trading environments by:

- Generating and broadcasting random trading orders
- Managing real-time orderbook state
- Handling authenticated user orders via Firebase
- Supporting multiple ticker subscriptions
- Providing comprehensive order validation and error handling

## Features

### Core Functionality

- **Real-time WebSocket Server** - High-performance async WebSocket server
- **Authenticated Order Placement** - Firebase JWT token validation for user orders
- **Automatic Order Generation** - Configurable random order simulation
- **Orderbook Management** - Live bid/ask tracking with price-level aggregation
- **Multi-ticker Support** - Subscribe to specific trading symbols
- **Batch Data Delivery** - Initial orderbook snapshots for new connections

### Architecture

- **Modular Design** - Abstract base broadcaster for extensibility
- **Async/Await** - Modern Python asyncio for high concurrency
- **Thread-safe Operations** - Proper locking for concurrent order processing
- **Subscription Management** - Per-ticker client subscription tracking

## Requirements

- **Python 3.8+**
- **Firebase Admin SDK**
- **WebSockets library**
- **NumPy**

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/asavy79/marketdata-simulator.git
   cd order-simulator
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Firebase**
   - Place your Firebase service account JSON file as `service-account.json` in the project root
   - Ensure your Firebase project has authentication enabled

## Usage

### Quick Start

Start the simulator with default configuration:

```bash
python -m src.main
```

This launches a WebSocket server on `ws://localhost:8765` that:

- Broadcasts random QNTX orders every 30 seconds
- Accepts authenticated user orders
- Maintains live orderbook state in memory

### WebSocket Connection

#### Subscribe to a Ticker

Connect to `ws://localhost:8765/QNTX` to subscribe to QNTX orders.

### Configuration

Modify `src/main.py` to customize the simulator:

```python
order_broadcaster = OrderBroadcaster(
    host="localhost",              # WebSocket server host
    port=8765,                    # WebSocket server port
    interval=30,                  # Broadcast interval (seconds)
    price_lower_bound=10,         # Minimum order price
    price_upper_bound=20,         # Maximum order price
    ticker="QNTX",               # Primary ticker symbol
    auth_service=auth_service,    # Firebase auth service
    tickers=["QNTX"]             # Supported ticker list
)
```

### Project Structure

```
src/
├── broadcasters/
│   ├── base_broadcaster.py      # Abstract WebSocket broadcaster
│   └── order_broadcaster.py     # Trading order implementation
├── services/
│   └── auth/
│       ├── auth_service.py      # Authentication interface
│       └── firebase_auth_service.py  # Firebase implementation
├── utils/
│   └── generators.py           # Order generation utilities
└── main.py                     # Application entry point

tests/
├── connection_test.py          # WebSocket connection tests
└── order_test.py              # Order processing tests
```

## License

This project is part of the QuantX trading platform ecosystem.
