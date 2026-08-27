import pytest
from functools import partial
from main import mirror


def test_normal_function():
    def greet(name: str, age: int = 18, *, excited: bool = False) -> str:
        """跟某人打招呼。"""
        return f"hi {name}, age {age}, excited={excited}"

    info = mirror(greet)
    assert info.name == "greet"
    assert info.qualname == "test_normal_function.<locals>.greet"
    assert info.signature is not None
    assert info.annotations["name"] is str
    assert info.annotations["age"] is int
    assert info.annotations["excited"] is bool
    assert info.annotations["return"] is str
    assert info.defaults == (18,)
    assert info.kwdefaults == {"excited": False}
    assert info.is_coroutine is False
    assert info.is_async_generator is False
    assert info.doc == "跟某人打招呼。"
    assert info.source is not None and "def greet" in info.source


def test_nested_qualname():
    def outer():
        def inner(x: int) -> int:
            return x
        return inner

    info = mirror(outer())
    assert info.name == "inner"
    assert info.qualname == "test_nested_qualname.<locals>.outer.<locals>.inner"


def test_no_defaults():
    def f(a, b, c):
        return a

    info = mirror(f)
    assert info.defaults == ()  # 没有默认值 -> 空 tuple，而不是 None
    assert info.kwdefaults is None


def test_coroutine():
    async def f():
        pass
    assert mirror(f).is_coroutine is True


def test_async_generator():
    async def f():
        yield 1
    assert mirror(f).is_async_generator is True
    assert mirror(f).is_coroutine is False


def test_builtin_source_is_none():
    info = mirror(len)
    assert info.name == "len"
    assert info.signature is not None
    assert info.source is None  # C 实现没有源码


def test_partial():
    def add(a: int, b: int = 1) -> int:
        """add two numbers."""
        return a + b

    info = mirror(partial(add, 10))
    assert info.name == "partial"
    # 注解从有效签名推导：a 已被绑定，只剩 b 和 return
    assert info.annotations == {"b": int, "return": int}
    assert info.source is None  # partial 是 C 类型，没有源码
    assert info.signature is not None


def test_callable_instance():
    class Fancy:
        def __call__(self, x: int) -> int:
            return x

    info = mirror(Fancy())
    assert info.name == "Fancy"  # 没 __name__，退回类名
    # 注解来自 __call__ 的签名，而不是空
    assert info.annotations == {"x": int, "return": int}
    assert info.signature is not None


def test_class_itself():
    class Point:
        x: int
        y: int

        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y

    info = mirror(Point)
    assert info.name == "Point"
    # 类是 callable，签名对应构造器
    assert info.signature is not None
    params = list(info.signature.parameters)
    assert "x" in params and "y" in params


def test_lambda():
    f = lambda a, b=2: a + b  # noqa: E731
    info = mirror(f)
    assert info.name == "<lambda>"
    assert info.defaults == (2,)
    assert info.doc is None


def test_signature_failure_is_none():
    # int / dict / type 等 C 类型无法推导签名，应返回 None 而不抛异常
    for c in (int, dict, type):
        info = mirror(c)
        assert info.signature is None
        assert info.name == c.__name__
