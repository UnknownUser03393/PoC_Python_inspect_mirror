import inspect
from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    _func: Callable

    def _attr(self, *names: str) -> Any:
        for n in names:
            if (val := getattr(self._func, n, None)) is not None: return val
        return None

    @property
    def name(self) -> str:
        return self._attr("__name__", "__qualname__") or type(self._func).__name__

    @property
    def qualname(self) -> str:
        return self._attr("__qualname__", "__name__") or self.name

    @property
    def signature(self) -> inspect.Signature | None:
        try:
            signature = inspect.signature(self._func)
        except (ValueError, TypeError):
            signature = None

        return signature

    @property
    def annotations(self) -> dict[str, Any]:
        sign = self.signature
        if sign is not None:
            annotations = {
                pname: p.annotation
                for pname, p in sign.parameters.items()
                if p.annotation is not inspect.Parameter.empty
            }
            if sign.return_annotation is not inspect.Signature.empty:
                annotations["return"] = sign.return_annotation
        else:
            annotations = {}

        return annotations

    @property
    def defaults(self) -> tuple[Any, ...]:
        return self._attr("__defaults__") or ()

    @property
    def kwdefaults(self) -> dict[str, Any]:
        return self._attr("__kwdefaults__") or {}

    @property
    def is_coroutine(self) -> bool:
        return inspect.iscoroutinefunction(self._func)

    @property
    def is_async_generator(self) -> bool:
        return inspect.isasyncgenfunction(self._func)

    @property
    def doc(self) -> str | None:
        try:
            return inspect.getdoc(self._func)
        except (ValueError, TypeError):
            return None

    @property
    def source(self) -> str | None:
        try:
            return inspect.getsource(self._func)
        except (OSError, TypeError):
            return None