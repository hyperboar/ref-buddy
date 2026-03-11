from app import sio

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"Received message from {sid}: {data}")
    await sio.emit("response", f"Server got: {data}", to=sid)

@sio.event
async def join(sid, room):
    print(f"{sid} joined room: {room}")
    await sio.emit("response", f"{sid} joined room {room}", to=sid)