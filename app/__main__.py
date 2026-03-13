import uvicorn

from app.utils.misc import is_debugging
from shared_utils.Env import Env

if is_debugging():
    from app import app_quart
    app_quart.run(host='0.0.0.0', port=int(Env.SERVER_PORT))
else:
    uvicorn.run('app.here_you_go_uvicorn:asgi_app', host='0.0.0.0', port=int(Env.SERVER_PORT), reload=False, lifespan="off")