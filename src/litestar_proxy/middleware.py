"""HTTP Proxy middleware factory function"""

from litestar.enums import ScopeType
from litestar.middleware import AbstractMiddleware
from litestar.types import HTTPScope, Receive, Scopes, Send
from litestar.types.asgi_types import ASGIApp

from litestar_proxy._utils import create_proxy_request, create_response, send_request
from litestar_proxy.config import HttpProxyConfig


def create_http_proxy_middelware(config: HttpProxyConfig) -> type[AbstractMiddleware]:
    """
    The middleware factory function that takes a HttpProxy config and creates the configured
    ASGI middleware.
    """

    class HttpProxyMiddleware(AbstractMiddleware):
        """
        HTTP Proxy middleware that proxies all request to the URL given in the config and processes
        the request and response based on the configuration
        """

        scopes = {ScopeType.HTTP}
        exclude_opt_key = "exclude_from_http_proxy"

        def __init__(
            self,
            app: ASGIApp,
            exclude: str | list[str] | None = None,
            exclude_opt_key: str | None = None,
            scopes: Scopes | None = None,
        ) -> None:
            """
            Initialize the middleware using the AbstractMiddleware logic and set the config
            """
            self.config = config
            super().__init__(app, exclude, exclude_opt_key, scopes)

        async def __call__(self, scope: HTTPScope, receive: Receive, send: Send):
            """
            Call the middleware. Proxy all requests to the target URL and return the response
            directly, bypassing the handler
            """
            response = create_response(
                self.config,
                await send_request(await create_proxy_request(self.config, scope, receive)),
            )
            await response(scope, receive, send)

    return HttpProxyMiddleware
