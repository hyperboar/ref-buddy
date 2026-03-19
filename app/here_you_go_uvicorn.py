# This file is a workaround so uvicorn can find asgi_app object using uvicorn.run().
# Only an import here.
import socketio

from app import create_app, create_sio

app_quart = create_app()
sio = create_sio()
asgi_app = socketio.ASGIApp(sio, app_quart)