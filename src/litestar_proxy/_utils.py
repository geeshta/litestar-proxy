from urllib.parse import urlunsplit

from httpx import AsyncClient
from httpx import Request as HttpxRequest
from httpx import Response as HttpxResponse
from litestar.response.base import ASGIResponse
from litestar.types import HTTPScope, Receive

from litestar_proxy.config import HttpProxyConfig
from litestar_proxy.headers import HeaderMaker
from litestar_proxy.url import make_urls


async def send_request(request: HttpxRequest) -> HttpxResponse:
    async with AsyncClient() as client:
        return await client.send(request)


async def get_body_content(receive: Receive) -> bytes:
    """
    Extract the request body from ASGI Send message
    """
    body = bytearray()
    more_body = True

    while more_body:
        event = await receive()
        if event["type"] == "http.request":
            body.extend(event["body"])
            more_body = event["more_body"]

    return bytes(body)


async def create_proxy_request(
    config: HttpProxyConfig, scope: HTTPScope, receive: Receive
) -> HttpxRequest:
    """
    Create the request to the target server given a HttpProxyConfig
    """
    urls = make_urls(config.url, config, scope)
    url = urlunsplit(urls["final_url"])

    content = await get_body_content(receive)

    header_maker = HeaderMaker(scope, config.request_header_config.header_parser)
    headers = header_maker.update_value(
        "content-length",
        f"{len(content)}",
        when=len(content) > 0 or "content-length" in header_maker.headers,
    ).to_request_headers(config.request_header_config, urls)

    method = scope["method"]

    return HttpxRequest(method=method, url=url, content=content, headers=headers)


def create_response(config: HttpProxyConfig, response: HttpxResponse) -> ASGIResponse:
    """
    Process the response from the target server given a HttpProxyConfig and return ASGIResponse
    of Litestar
    """
    res_headers = HeaderMaker(
        response.headers, config.response_header_config.header_parser
    ).to_response_headers(config.response_header_config)

    if config.response_header_config.exclude_cookies:
        cookies = None
    else:
        cookies = {}
        cookies.update(response.cookies)

    return ASGIResponse(
        body=response.content,
        content_length=len(response.content),
        headers=res_headers.items(),
        encoding=(response.encoding or "utf-8"),
        status_code=response.status_code,
        cookies=cookies,
    )
