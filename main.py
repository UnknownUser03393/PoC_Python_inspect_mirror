import inspect
from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    name: str
    qualname: str
    signature: inspect.Signature | None
    annotations: dict[str, Any]
    defaults: tuple[Any, ...]
    kwdefaults: dict[str, Any] | None
    is_coroutine: bool
    is_async_generator: bool
    doc: str | None
    source: str | None


def mirror(func: Callable) -> FunctionInfo:
    def _attr(obj: Any, *names: str) -> Any:
        for n in names:
            if (val := getattr(obj, n, None)) is not None: return val
        return None

    name = _attr(func, "__name__", "__qualname__") or type(func).__name__
    qualname = _attr(func, "__qualname__", "__name__") or name

    try:
        signature = inspect.signature(func)
    except (ValueError, TypeError):
        signature = None

    annotations = _attr(func, "__annotations__") or {}

    defaults = _attr(func, "__defaults__")
    if defaults is None: defaults = ()
    kwdefaults = _attr(func, "__kwdefaults__")
    is_coroutine = inspect.iscoroutinefunction(func)
    is_async_generator = inspect.isasyncgenfunction(func)

    try:
        doc = inspect.getdoc(func)
    except (ValueError, TypeError):
        doc = None

    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        source = None

    return FunctionInfo(
        name=name,
        qualname=qualname,
        signature=signature,
        annotations=annotations,
        defaults=defaults,
        kwdefaults=kwdefaults,
        is_coroutine=is_coroutine,
        is_async_generator=is_async_generator,
        doc=doc,
        source=source,
    )


if __name__ == "__main__":  # pragma: no cover
    def greet(name: str, age: int = 18, *, excited: bool = False) -> str:
        """跟某人打招呼。"""
        return f"hi {name}, age {age}, excited={excited}"

    info = mirror(greet)
    print(f"name            = {info.name!r}")
    print(f"qualname        = {info.qualname!r}")
    print(f"signature       = {info.signature}")
    print(f"annotations     = {info.annotations}")
    print(f"defaults        = {info.defaults}")
    print(f"kwdefaults      = {info.kwdefaults}")
    print(f"is_coroutine    = {info.is_coroutine}")
    print(f"is_async_gen    = {info.is_async_generator}")
    print(f"doc             = {info.doc!r}")
    print(f"source (first)  = {info.source.splitlines()[0] if info.source else None!r}")

    # 鲁棒性：对 partial / 类 / C 内建函数也不崩。
    from functools import partial
    def add(a: int, b: int = 1) -> int:
        """add two numbers."""
        return a + b

    partial_add = partial(add, 10)
    print("\n-- partial --")
    p = mirror(partial_add)
    print(f"name        = {p.name!r}")
    print(f"signature   = {p.signature}")
    print(f"annotations = {p.annotations}")
    print(f"defaults    = {p.defaults}")

    print("\n-- builtin --")
    ln = mirror(len)
    print(f"name        = {ln.name!r}")
    print(f"signature   = {ln.signature}")
    print(f"source      = {ln.source!r}")
