from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.vehicles import Vehicle


class IInventoryItem(ABC):
    """Интерфейс для всех объектов (транспорта и вещей), ставящихся на баланс парка"""

    @property
    @abstractmethod
    def inventory_number(self) -> int:
        """Уникальный инвентарный номер объекта"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Наименование модели или предмета"""
        pass


class IEnergyConsumer(ABC):
    """Интерфейс для любых устройств, потребляющих электроэнергию"""

    @property
    @abstractmethod
    def daily_energy_kwh(self) -> float:
        """Суточный расход электроэнергии в кВт·ч"""
        pass


class IServiceCenter(ABC):
    """Интерфейс сервиса техосмотра для проверки транспорта перед приёмкой в парк"""

    @abstractmethod
    def inspect(self, vehicle: Vehicle) -> bool:
        """Возвращает True, если транспорт исправен и допущен к эксплуатации"""
        pass
