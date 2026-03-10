import uvicorn

from shared_utils.Env import Env

uvicorn.run('app.here_you_go_uvicorn:asgi_app', host='0.0.0.0', port=int(Env.SERVER_PORT), reload=False, lifespan="off")