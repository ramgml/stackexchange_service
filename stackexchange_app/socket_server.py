import asyncio
import websockets
from stackexchange_app.settings import WS_SERVER_URL


async def producer(message):
    async with websockets.connect(WS_SERVER_URL) as ws:
        await ws.send(message)
        await ws.recv()


class Server:
    clients = set()

    async def register(self, ws):
        self.clients.add(ws)

    async def unregister(self, ws):
        self.clients.remove(ws)

    async def send_to_clients(self, message):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def distribute(self, ws):
        async for message in ws:
            await self.send_to_clients(message)

    async def ws_handler(self, ws, uri):
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)


server = Server()

if __name__ == '__main__':
    start_server = websockets.serve(server.ws_handler, host='0.0.0.0', port=4000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
