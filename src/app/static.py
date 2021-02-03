from starlette.middleware.gzip import GZipMiddleware
from starlette.staticfiles import StaticFiles

static = StaticFiles(directory="static")
app = GZipMiddleware(static)
