from litestar import Litestar, Response, get


@get("/")
async def index() -> Response:
    return Response({"status": "ok"})


app = Litestar(route_handlers=[index])
