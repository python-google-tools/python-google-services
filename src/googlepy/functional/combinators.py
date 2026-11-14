"""Functional combinators and composition utilities.

Provides pipe, compose, and curry primitives for assembling stateless,
declarative transformation pipelines over Google API resources.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def pipe(value: T, *callables: Callable[[Any], Any]) -> Any:
    """Pass a value sequentially through a series of unary functions (left-to-right).

    Args:
        value: The initial input value.
        *callables: Unary functions to apply in sequence.

    Returns:
        The final transformed result.

    Example:
        >>> pipe(
        ...     "file_123",
        ...     lambda id: f"files/{id}",
        ...     client.get,
        ...     lambda res: res.get("name")
        ... )
    """
    result = value
    for fn in callables:
        result = fn(result)
    return result


def compose(*callables: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose multiple unary functions into a single function (right-to-left).

    Args:
        *callables: Functions to compose.

    Returns:
        A callable representing f(g(h(...(x)))).

    Example:
        >>> get_title = compose(lambda doc: doc.get("title", ""), client.get)
    """
    if not callables:
        return lambda x: x

    def composed(arg: Any) -> Any:
        res = arg
        for fn in reversed(callables):
            res = fn(res)
        return res

    return composed


def curry(func: Callable[..., R]) -> Callable[..., Any]:
    """Curry a function to allow partial application until all required arguments are met.

    Args:
        func: The function to curry.

    Returns:
        A curried version of the function.
    """
    import inspect

    sig = inspect.signature(func)
    required_count = len([
        p for p in sig.parameters.values()
        if p.default == inspect.Parameter.empty
        and p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ])

    @functools.wraps(func)
    def curried(*args: Any, **kwargs: Any) -> Any:
        if len(args) + len(kwargs) >= required_count:
            return func(*args, **kwargs)
        return lambda *more_args, **more_kwargs: curried(
            *(args + more_args), **{**kwargs, **more_kwargs}
        )

    return curried
