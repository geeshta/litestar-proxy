"""Configuration objects for the litestar proxy"""

from collections.abc import Iterable
from dataclasses import dataclass, field

from litestar_proxy.types import (
    HeaderParser,
    PathStrategy,
    QueryStrategy,
    SchemeStrategy,
)


@dataclass(slots=True, frozen=True)
class ResponseHeaderConfig:
    exclude_cookies: bool = False
    exclude_headers: Iterable[str] = field(default_factory=list)
    header_parser: HeaderParser = lambda x: x


@dataclass(slots=True, frozen=True)
class RequestHeaderConfig(ResponseHeaderConfig):
    override_host: bool = True


@dataclass(slots=True, frozen=True)
class HttpProxyConfig:
    url: str
    scheme_strategy: SchemeStrategy = "no-downgrade"
    path_strategy: PathStrategy = "append"
    query_strategy: QueryStrategy = "merge"
    request_header_config: RequestHeaderConfig = field(default_factory=RequestHeaderConfig)
    response_header_config: ResponseHeaderConfig = field(default_factory=ResponseHeaderConfig)
