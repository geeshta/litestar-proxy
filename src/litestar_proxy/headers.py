"""Classes and functions for HTTP header processing"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Self, overload

from httpx import Headers as HttpxHeaders
from litestar.datastructures.headers import MutableScopeHeaders
from litestar.types.asgi_types import HeaderScope

from litestar_proxy.config import RequestHeaderConfig, ResponseHeaderConfig
from litestar_proxy.types import HeaderParser, URLs


def conditional(method: Callable[..., HeaderMaker]):
    """
    Decorator that allows to conditionally apply a method based on the `when` boolean parameter.
    If it is false, the method behaves like an identity function
    """

    def new_method(self, *args, when=True, **kwargs) -> HeaderMaker:
        if not when:
            return self
        return method(self, *args, **kwargs)

    return new_method


class HeaderMaker:
    """
    Utility class that applies given configuration to headers and prepares them for a request or
    a response
    """

    __slots__ = "headers"

    def __init__(self, scope: HeaderScope | HttpxHeaders, parser: HeaderParser) -> None:
        """
        Load headers form a HeaderScope of LiteStar or Headers of httpx and apply the provided
        parsing function
        """
        if isinstance(scope, HttpxHeaders):
            headers = MutableScopeHeaders()
            headers.update(scope)
        else:
            headers = MutableScopeHeaders(scope)
        parsed_headers = parser(headers)
        new_headers = MutableScopeHeaders()
        new_headers.update(parsed_headers)
        self.headers = new_headers

    @overload
    def filter_keys(self, keys: Iterable[str]) -> Self: ...
    @overload
    def filter_keys(self, keys: Iterable[str], when: bool) -> Self: ...
    @conditional
    def filter_keys(self, keys: Iterable[str]) -> Self:
        """
        Filter out all headers with the specified keys
        """
        for key in keys:
            if key in self.headers:
                del self.headers[key]
        return self

    @overload
    def update_value(self, key: str, value: str) -> Self: ...
    @overload
    def update_value(self, key: str, value: str, when: bool) -> Self: ...
    @conditional
    def update_value(self, key: str, value: str) -> Self:
        """
        Update the value of a given header
        """
        self.headers[key] = value
        return self

    def to_request_headers(self, config: RequestHeaderConfig, urls: URLs) -> MutableScopeHeaders:
        """
        Apply processing for request headers and return the resulting MutableScopeHeaders
        """
        return (
            self.update_value(
                key="host", value=urls["target_url"].netloc, when=config.override_host
            )
            .filter_keys(keys=["cookie"], when=config.exclude_cookies)
            .filter_keys(keys=config.exclude_headers)
            .headers
        )

    def to_response_headers(self, config: ResponseHeaderConfig) -> MutableScopeHeaders:
        """
        Apply processing for response headers and return the resulting MutableScopeHeaders
        """
        return (
            self.filter_keys("set-cookie", when=config.exclude_cookies)
            .filter_keys(config.exclude_headers)
            .headers
        )
