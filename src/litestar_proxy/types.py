"""Supporting type library for litestar proxy"""

from collections.abc import Callable, Iterable, Mapping
from typing import Literal, TypedDict
from urllib.parse import SplitResult

from litestar.datastructures.headers import MutableScopeHeaders

type OverrideStrategy = Literal["target", "request"]
type PathStrategy = OverrideStrategy | Literal["append"]
type QueryStrategy = OverrideStrategy | Literal["merge"]
type SchemeStrategy = OverrideStrategy | Literal["no-downgrade"]

type SupportsUpdate = Mapping[str, str] | Iterable[tuple[str, str]]
type HeaderParser = Callable[[MutableScopeHeaders], SupportsUpdate]


class URLs(TypedDict):
    request_url: SplitResult
    target_url: SplitResult
    final_url: SplitResult
