from pathlib import Path

from litestar import Litestar, Response, route

from litestar_proxy import HttpProxyConfig, create_http_proxy_middleware

proxy_config = HttpProxyConfig(url="http://127.0.0.1:5173")


@route(
    "/app",
    http_method=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    middleware=[create_http_proxy_middleware(proxy_config)],
)
async def index() -> Response:
    return Response({"status": "ok"})


@route(
    "/app/{path:path}",
    http_method=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    middleware=[create_http_proxy_middleware(proxy_config)],
)
async def frontend(path: Path) -> Response:
    return Response({"status": "ok"})


app = Litestar(route_handlers=[frontend, index])
