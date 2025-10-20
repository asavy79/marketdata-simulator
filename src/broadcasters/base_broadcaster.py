import websockets
import asyncio
from abc import ABC, abstractmethod
import json


class BaseBroadcaster(ABC):

    def __init__(self, host, port, interval, timeout=None):
        self.interval = interval
        self.host = host
        self.port = port
        self.clients = set()
        self.timeout = timeout

    def start_server(self):
        asyncio.run(self.server_initializer())

    async def server_initializer(self):

        async with websockets.serve(self.handler, self.host, self.port):
            print("WebSocket server started on ws://localhost:8765")
            asyncio.create_task(self.broadcast_periodic())
            await asyncio.Future()

    async def handler(self, websocket):
        self.clients.add(websocket)
        await self.initial_connection_action(client=websocket)
        try:
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by client")
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_periodic(self):
        while True:
            await asyncio.sleep(self.interval)
            try:
                message = self.create_message()
                print(message)
            except Exception as e:
                print(e)
                message = {"error": e}

            await asyncio.gather(*[client.send(json.dumps(message)) for client in self.clients],
                                 return_exceptions=True)

    async def broadcast_batch(self, client):
        message = self.create_batch_message()
        # await client.send(json.dumps(message))
        await asyncio.gather(*[client.send(json.dumps(message)) for client in [client]])

    @abstractmethod
    async def initial_connection_action(self):
        pass

    @abstractmethod
    def create_batch_message(self):
        pass

    @abstractmethod
    def create_message(self) -> dict:
        pass
