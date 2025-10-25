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
            async for raw in websocket:
                msg = json.loads(raw)
                await self.on_message(msg, websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            print("Client disconnected")
            self.clients.discard(websocket)

    async def broadcast_periodic(self):
        while True:
            await asyncio.sleep(self.interval)
            try:
                message = self.create_message()
                print(message)
            except Exception as e:
                print(e)
                message = {"error": e}

            await self.broadcast_message(message)

    async def broadcast_message(self, message):
        await asyncio.gather(*[client.send(json.dumps(message)) for client in self.clients],
                             return_exceptions=True)

    async def broadcast_batch(self, client):
        message = self.create_batch_message()
        # await client.send(json.dumps(message))
        await client.send(json.dumps(message))

    @ abstractmethod
    async def initial_connection_action(self):
        pass

    @ abstractmethod
    def create_batch_message(self):
        pass

    @ abstractmethod
    def create_message(self) -> dict:
        pass

    @ abstractmethod
    def on_message(self, msg, websocket):
        pass
