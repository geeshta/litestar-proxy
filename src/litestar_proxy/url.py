"""Set of utilities for managing and resolving urls"""

from urllib.parse import SplitResult, urlencode, urljoin, urlsplit

from fast_query_parsers import parse_query_string
from litestar.types import HTTPScope

from litestar_proxy.config import HttpProxyConfig
from litestar_proxy.types import PathStrategy, QueryStrategy, SchemeStrategy, URLs


def resolve_netloc(server: tuple[str, int | None] | None) -> str:
    """
    Resolves the network location from the format provided by scope['server']
    """
    if server is None:
        return ""
    if server[1] is None:
        return server[0]
    return f"{server[0]}:{server[1]}"


def scheme_secure(scheme: str) -> bool:
    """
    Predicate whether a valid network scheme is provided and if it is secure
    """
    if scheme not in {"http", "https"}:
        raise ValueError("Scheme must be `http` or `https`")
    else:
        return scheme == "https"


def resolve_scheme(request_scheme: str, target_scheme: str, how: SchemeStrategy) -> str:
    """
    Decide what scheme should be used for the proxy request
    """
    request_secure = scheme_secure(request_scheme)
    target_secure = scheme_secure(target_scheme)

    match how:
        case "target":
            return target_scheme
        case "request":
            return request_scheme
        case "no-downgrade":
            return "https" if request_secure or target_secure else "http"


def resolve_paths(request_path: str, target_path: str, how: PathStrategy) -> str:
    """
    Decide what path should be used for the proxy request
    """
    target_path = target_path if target_path.endswith("/") else f"{target_path}/"
    request_path = request_path[1:] if request_path.startswith("/") else request_path

    match how:
        case "target":
            return target_path
        case "request":
            return request_path
        case "append":
            return urljoin(target_path, request_path)


def resolve_queries(request_query: bytes, target_query: bytes, how: QueryStrategy) -> str:
    """
    Decide what query string should be used for the proxy request
    """
    parsed_request = parse_query_string(request_query, "&")
    parsed_target = parse_query_string(target_query, "&")

    match how:
        case "target":
            return urlencode(parsed_target)
        case "request":
            return urlencode(parsed_request)
        case "merge":
            return urlencode(parsed_target + parsed_request)


def make_urls(target: str, config: HttpProxyConfig, scope: HTTPScope) -> URLs:
    """
    Build the URLs dict with the request URL, target URL and the resolved final URL base on the
    provided configuration
    """
    request_url = SplitResult(
        scheme=scope["scheme"],
        netloc=resolve_netloc(scope["server"]),
        path=scope["path"],
        query=scope["query_string"].decode(),
        fragment="",
    )
    target_url = urlsplit(target)

    final_url = SplitResult(
        scheme=resolve_scheme(request_url.scheme, target_url.scheme, config.scheme_strategy),
        netloc=target_url.netloc,
        path=resolve_paths(request_url.path, target_url.path, config.path_strategy),
        query=resolve_queries(
            scope["query_string"], target_url.query.encode(), config.query_strategy
        ),
        fragment="",
    )

    return {"request_url": request_url, "target_url": target_url, "final_url": final_url}
