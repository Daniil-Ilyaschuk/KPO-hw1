from __future__ import annotations
from abc import ABC
from domain.interfaces import IInventoryItem, IEnergyConsumer


class Equipment(IInventoryItem, ABC):
    """Базовый абстрактный класс для инвентарных вещей и оборудования парка"""

    def __init__(self, inventory_number: int, name: str) -> None:
        if inventory_number <= 0:
            raise ValueError("Инвентарный номер должен быть положительным числом")
        self._inventory_number = inventory_number
        self._name = name

    @property
    def inventory_number(self) -> int:
        return self._inventory_number

    @property
    def name(self) -> str:
        return self._name


class Helmet(Equipment):
    """Защитный шлем (ставится на баланс, энергию не потребляет)"""

    def __init__(self, inventory_number: int, name: str, size: str = "M") -> None:
        super().__init__(inventory_number, name)
        self.size = size


class ChargingStation(Equipment, IEnergyConsumer):
    """Зарядная док-станция / шкаф (вещь на балансе, потребляющая электроэнергию)"""

    def __init__(
        self,
        inventory_number: int,
        name: str,
        daily_energy_kwh: float,
        ports_count: int = 8,
    ) -> None:
        super().__init__(inventory_number, name)
        if daily_energy_kwh < 0:
            raise ValueError("Суточный расход энергии не может быть отрицательным")
        self._daily_energy_kwh = float(daily_energy_kwh)
        self.ports_count = ports_count

    @property
    def daily_energy_kwh(self) -> float:
        return self._daily_energy_kwh
