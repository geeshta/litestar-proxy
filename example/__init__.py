from pathlib import Path

from litestar import Litestar, Response, route

from litestar_proxy import HttpProxyConfig, create_http_proxy_middleware

proxy_config = HttpProxyConfig(url="http://127.0.0.1:5173")
proxy_middleware = create_http_proxy_middleware(proxy_config)


@route(
    "/app",
    http_method=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    middleware=[proxy_middleware],
)
async def index() -> Response:
    return Response({"message": "This will never be reached"})


@route(
    "/app/{path:path}",
    http_method=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    middleware=[proxy_middleware],
)
async def frontend(path: Path) -> Response:
    return Response({"message": "This will never be reached"})


app = Litestar(route_handlers=[frontend, index])
