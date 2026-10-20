from __future__ import annotations
from abc import ABC
from domain.interfaces import IInventoryItem, IEnergyConsumer


class Vehicle(IInventoryItem, ABC):
    """Базовый абстрактный класс для любого транспортного средства"""

    def __init__(
        self,
        inventory_number: int,
        name: str,
        simplicity_rating: int,
        is_technically_sound: bool = True,
    ) -> None:
        if inventory_number <= 0:
            raise ValueError("Инвентарный номер должен быть положительным числом")
        if not (1 <= simplicity_rating <= 10):
            raise ValueError("Характеристика 'простота для новичка' должна быть от 1 до 10")

        self._inventory_number = inventory_number
        self._name = name
        self._simplicity_rating = simplicity_rating
        self._is_technically_sound = is_technically_sound

    @property
    def inventory_number(self) -> int:
        return self._inventory_number

    @property
    def name(self) -> str:
        return self._name

    @property
    def simplicity_rating(self) -> int:
        """Оценка простоты управления для новичка (по шкале 1–10)"""
        return self._simplicity_rating

    @property
    def is_technically_sound(self) -> bool:
        """Техническая исправность (используется при прохождении техосмотра)"""
        return self._is_technically_sound


class ElectricVehicle(Vehicle, IEnergyConsumer, ABC):
    """Базовый класс для электротранспорта (потребляет энергию)"""

    def __init__(
        self,
        inventory_number: int,
        name: str,
        simplicity_rating: int,
        daily_energy_kwh: float,
        is_technically_sound: bool = True,
    ) -> None:
        super().__init__(inventory_number, name, simplicity_rating, is_technically_sound)
        if daily_energy_kwh < 0:
            raise ValueError("Суточный расход энергии не может быть отрицательным")
        self._daily_energy_kwh = float(daily_energy_kwh)

    @property
    def daily_energy_kwh(self) -> float:
        return self._daily_energy_kwh


class KickScooter(ElectricVehicle):
    """Электросамокат"""

    def __init__(
        self,
        inventory_number: int,
        name: str,
        simplicity_rating: int,
        daily_energy_kwh: float,
        has_seat: bool = False,
        is_technically_sound: bool = True,
    ) -> None:
        super().__init__(
            inventory_number, name, simplicity_rating, daily_energy_kwh, is_technically_sound
        )
        self.has_seat = has_seat


class ElectricBike(ElectricVehicle):
    """Электровелосипед"""

    def __init__(
        self,
        inventory_number: int,
        name: str,
        simplicity_rating: int,
        daily_energy_kwh: float,
        max_assist_speed_kmh: int = 25,
        is_technically_sound: bool = True,
    ) -> None:
        super().__init__(
            inventory_number, name, simplicity_rating, daily_energy_kwh, is_technically_sound
        )
        self.max_assist_speed_kmh = max_assist_speed_kmh


class MechanicalBike(Vehicle):
    """Обычный механический велосипед (не потребляет электроэнергию)"""

    def __init__(
        self,
        inventory_number: int,
        name: str,
        simplicity_rating: int,
        gears_count: int = 7,
        is_technically_sound: bool = True,
    ) -> None:
        super().__init__(inventory_number, name, simplicity_rating, is_technically_sound)
        self.gears_count = gears_count
