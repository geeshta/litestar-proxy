# Litestar Proxy

Proxy middleware for the [Litestar web framework](https://github.com/litestar-org/litestar).

## Usage

The following example will redirect all requests to `/app` and nested paths to `http://127.0.0.1:5173`
and update the `Host` header. It will proxy all cookies both sent by the client and by the target server.

The handler logic will never be executed, so it does not matter, what happens inside the handler
function.

```python
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

```

## Configuration

### HttpProxyConfig

A class that holds the configuration for the middleware.
Params:

- `url` - The target URL to proxy the requests to. This parameter is **required**
- `scheme_strategy` - The strategy for resolving the proxied request scheme
  - `no-downgrade` _(default)_ - Always use HTTPS except for when both the target and incoming
  request scheme is HTTP
  - `target` - always use the scheme of the target server
  - `request` - always use the scheme of the incoming request
- `path_strategy` - The strategy for resolving the proxied request path
  - `append` _(default)_ - append the request path to the target URL
  - `target` - always use the target path, discard the request path
  - `request` - always use the incoming request path, discard the target path
- `query_strategy` - The strategy for resolving the proxied request query string
  - `merge` _(default)_ - Merge the query parameters of the target URL and incoming request
  - `target` - always use the target URL query params, discard the query params of the incoming
  request
  - `request` - always use the query params of the incoming request, discard the params of the
  target URL
  - `request_header_config` - how to handle the headers for the proxied request (see below)
  - `response_header_config` - how to handle the headers for the response from the target server
  (see below)

### RequestHeaderConfig

A class that holds the configuration for the headers of the proxied request
Params:

- `override_host` - whether to override the Host header to the target server location _(default True)_
- `exclude_cookies` - whether to exclude cookies when proxying the incoming request _(default False)_
- `exclude_headers` - a list of header names to exclude from the proxied request
- `header_parser` - a callable that takes the `MutableScopeHeader` class of Litestar which contains
the original headers, and returns an object that can be passed into the `.update()` function of
`MutableMapping` - so either a `Mapping[str, str]` or `Iterable[Tuple[str, str]]`

### ResponseHeaderConfig

A class that holds the configuration for the headers of the response from the target URL
Params:

Same as `RequestHeaderConfig` except it doesn't have the `override_host` option

### Example

The following example behaves similarly as the default, but it also

- Excludes cookies from both response and request
- Excludes the `Origin` header from the response
- Uses a custom parsing function to remov all headers that start with `X-Secret` from both the
request and the response

```python
from litestar_proxy import HttpProxyConfig, RequestHeaderConfig, ResponseHeaderConfig

config = HttpProxyConfig(
    url="http://127.0.0.1:5173",
    scheme_strategy="no-downgrade",
    path_strategy="append",
    query_strategy="merge",
    request_header_config=RequestHeaderConfig(
        override_host=True,
        exclude_cookies=True,
        exclude_headers=["Origin"],
        header_parser=lambda headers: {
            k: v for k, v in headers.items() if not str(k).lower().startswith("X-Secret")
        },
    ),
    response_header_config=ResponseHeaderConfig(
        exclude_cookies=True,
        header_parser=lambda headers: {
            k: v for k, v in headers.items() if not str(k).lower().startswith("X-Secret")
        },
    ),
)
```
