# Order Simulator

A WebSocket-based order simulator that generates and broadcasts random trading orders for testing and development purposes.

## Overview

This project simulates trading orders by generating random buy/sell orders with configurable price ranges and broadcasting them to connected WebSocket clients. It's designed to help test trading applications and orderbook systems.

## Features

- WebSocket server for real-time order broadcasting
- Configurable price ranges and ticker symbols
- Random order generation (buy/sell orders with price, quantity, and timestamp)
- Periodic broadcasting at configurable intervals
- Support for multiple connected clients

## Requirements

- Python 3.7+
- websockets
- numpy

## Installation

1. Clone or download the project
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the simulator with default settings:

```bash
python -m src.main
```

This will start a WebSocket server on `localhost:8765` that broadcasts random QNTX orders every second with prices between $10-20.

### Configuration

The simulator can be configured by modifying the parameters in `src/main.py`:

```python
order_broadcaster = OrderBroadcaster(
    host="localhost",           # WebSocket server host
    port=8765,                 # WebSocket server port
    interval=1,                # Broadcast interval in seconds
    price_lower_bound=10,      # Minimum order price
    price_upper_bound=20,      # Maximum order price
    ticker="QNTX"             # Stock ticker symbol
)
```

### Connecting to the WebSocket

Connect to `ws://localhost:8765` to receive order updates. Each message contains:

```json
{
    "type": "Buy" / "Sell",
    "price": 15.67,
    "quantity": 25,
    "ticker": "QNTX",
    "timestamp": "2025-09-30T..."
}
```

## Development

The project uses an abstract base class (`BaseBroadcaster`) that can be extended to create different types of data broadcasters. The `OrderBroadcaster` is one implementation that focuses on trading orders.

To create a custom broadcaster:

1. Extend `BaseBroadcaster`
2. Implement the `create_message()` method
3. Initialize with your desired parameters
