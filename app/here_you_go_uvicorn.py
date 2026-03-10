# This file is a workaround so uvicorn can find asgi_app object using uvicorn.run().
# Only an import here.

from app import asgi_app