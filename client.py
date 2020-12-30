import socketio
import asyncio

async def main():  

    sock = socketio.AsyncClient(logger = True)

    @sock.event
    async def connect():
        print("I'm connected!")

    @sock.event
    async def connect_error():
        print("The connection failed!")

    @sock.event
    async def disconnect():
        print("I'm disconnected!")

    await sock.connect(url = "http://0.0.0.0:8001")

    while True:
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())