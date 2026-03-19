import uvicorn

from app.utils.misc import is_debugging
from shared_utils.env import Env, is_testing

if not is_testing:
    from app import app_quart
    from app.models import DatabaseEnvironment
    from shared_utils.backup import make_database_backup
    app_quart.before_request(make_database_backup)
    DatabaseEnvironment.update_db_connection(is_testing)

if is_debugging():
    from app import app_quart
    app_quart.run(host='0.0.0.0', port=int(Env.SERVER_PORT))
else:
    uvicorn.run('app.here_you_go_uvicorn:asgi_app', host='0.0.0.0', port=int(Env.SERVER_PORT), reload=False, lifespan="off")