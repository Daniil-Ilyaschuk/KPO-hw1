from __future__ import annotations
from typing import Any, Callable, Dict, Type, TypeVar, get_type_hints

T = TypeVar("T")


class DIContainer:
    """Простой DI-контейнер с автоматическим внедрением зависимостей через конструктор"""

    def __init__(self) -> None:
        self._providers: Dict[Type[Any], Callable[[], Any]] = {}

    def register(self, abstraction: Type[T], implementation: Type[T]) -> None:
        """Регистрирует класс-реализацию для заданной абстракции (интерфейса)"""
        self._providers[abstraction] = lambda: self.resolve(implementation)

    def register_instance(self, abstraction: Type[T], instance: T) -> None:
        """Регистрирует готовый экземпляр (или mock/stub объект для тестирования)"""
        self._providers[abstraction] = lambda: instance

    def resolve(self, target_cls: Type[T]) -> T:
        """
        Создаёт экземпляр target_cls, автоматически разрешая все зависимости,
        указанные в аннотаций типов его конструктора (__init__)
        """
        if target_cls in self._providers:
            return self._providers[target_cls]()

        init_method = getattr(target_cls, "__init__", None)
        if init_method is None or init_method is object.__init__:
            return target_cls()

        type_hints = get_type_hints(init_method)
        kwargs: Dict[str, Any] = {}

        for param_name, param_type in type_hints.items():
            if param_name == "return":
                continue
            if param_type not in self._providers and not isinstance(param_type, type):
                raise KeyError(
                    f"Не удалось разрешить зависимость '{param_name}: {param_type}' "
                    f"для класса {target_cls.__name__}"
                )
            kwargs[param_name] = self.resolve(param_type)

        return target_cls(**kwargs)
