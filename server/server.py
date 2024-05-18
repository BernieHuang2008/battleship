import asyncio
import websockets
import random

from . import room

rooms = {}

def add_room():
    # generate a unique room id
    room_id = random.random()
    while room_id in rooms:
        room_id = random.random()
    
    # create a new room
    rooms[room_id] = Room(room_id)


async def handle_websocket(websocket, path):
    # Handle incoming WebSocket messages here
    async for message in websocket:
        # Process the received message
        print(f"Received message: {message}")

        # Send a response back to the client
        response = f"Received: {message}"
        await websocket.send(response)

async def serve():
    start_server = websockets.serve(handle_websocket, 'localhost', 8765)
    server = await start_server

    try:
        await asyncio.Future()  # Keep the server running indefinitely
    except KeyboardInterrupt:
        server.close()
        await server.wait_closed()

asyncio.run(serve())