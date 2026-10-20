from __future__ import annotations
from typing import List
from domain.interfaces import IInventoryItem, IEnergyConsumer, IServiceCenter
from domain.vehicles import Vehicle
from domain.equipment import Equipment


class FleetManager:
    """Сервис учёта парка техники и инвентарного имущества «ВышКат»"""

    NOVICE_SIMPLICITY_THRESHOLD = 6

    def __init__(self, service_center: IServiceCenter) -> None:
        # Зависимость внедряется извне
        self._service_center = service_center
        self._inventory: List[IInventoryItem] = []

    def _ensure_unique_inventory_number(self, number: int) -> None:
        if any(item.inventory_number == number for item in self._inventory):
            raise ValueError(
                f"Объект с инвентарным номером #{number} уже числится на балансе"
            )

    def try_add_vehicle(self, vehicle: Vehicle) -> bool:
        """
        Отправляет транспорт на техосмотр и ставит на баланс при успешной проверке
        Возвращает True, если транспорт принят в парк, иначе False
        """
        self._ensure_unique_inventory_number(vehicle.inventory_number)

        if not self._service_center.inspect(vehicle):
            return False

        self._inventory.append(vehicle)
        return True

    def add_equipment(self, equipment: Equipment) -> None:
        """Ставит на баланс инвентарную вещь (шлем, зарядную станцию и т.д.)"""
        self._ensure_unique_inventory_number(equipment.inventory_number)
        self._inventory.append(equipment)

    def get_all_inventory(self) -> List[IInventoryItem]:
        """Возвращает полный список техники и вещей на балансе"""
        return list(self._inventory)

    def get_vehicles(self) -> List[Vehicle]:
        """Возвращает только принятые в парк транспортные средства"""
        return [item for item in self._inventory if isinstance(item, Vehicle)]

    def get_equipment(self) -> List[Equipment]:
        """Возвращает только вещи и оборудование на балансе"""
        return [item for item in self._inventory if isinstance(item, Equipment)]

    def get_total_daily_energy_kwh(self) -> float:
        """
        Считает суммарное суточное энергопотребление парка (кВт·ч)
        Учитывает все объекты, реализующие IEnergyConsumer (электротранспорт и зарядные станции)
        """
        return sum(
            item.daily_energy_kwh
            for item in self._inventory
            if isinstance(item, IEnergyConsumer)
        )

    def get_novice_friendly_vehicles(self) -> List[Vehicle]:
        """
        Возвращает список прокатной техники, подходящей для новичков
        (характеристика 'простота для новичка' >= 6)
        """
        return [
            vehicle
            for vehicle in self.get_vehicles()
            if vehicle.simplicity_rating >= self.NOVICE_SIMPLICITY_THRESHOLD
        ]
