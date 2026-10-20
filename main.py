from __future__ import annotations
from domain.interfaces import IServiceCenter, IEnergyConsumer
from domain.vehicles import KickScooter, ElectricBike, MechanicalBike, Vehicle
from domain.equipment import Helmet, ChargingStation
from services.service_center import DefaultServiceCenter
from services.fleet_manager import FleetManager
from services.container import DIContainer


def try_register_vehicle(fleet: FleetManager, vehicle: Vehicle) -> None:
    """Вспомогательная функция для наглядного вывода процесса приёмки транспорта"""
    try:
        accepted = fleet.try_add_vehicle(vehicle)
        status = (
            "ПРИНЯТ В ПАРК (техосмотр пройден)"
            if accepted
            else "ОТКЛОНЁН (не прошёл техосмотр)"
        )
        print(
            f"  [Транспорт] #{vehicle.inventory_number} «{vehicle.name}» "
            f"(простота: {vehicle.simplicity_rating}/10) -> {status}"
        )
    except ValueError as err:
        print(f"  [Ошибка учёта] #{vehicle.inventory_number} «{vehicle.name}» -> {err}")


def main() -> None:
    print("=" * 72)
    print("  СИСТЕМА УЧЁТА ПАРКА КИКШЕРИНГА «ВышКат» («Доедем до дедлайна»)")
    print("=" * 72)

    # Инициализация DI-контейнера и разрешение зависимостей
    container = DIContainer()
    container.register(IServiceCenter, DefaultServiceCenter)
    fleet = container.resolve(FleetManager)

    # Сценарий приёмки транспортных средств через техосмотр
    print("\n1. ПРИЁМКА ТРАНСПОРТНЫХ СРЕДСТВ И ТЕХОСМОТР:")
    vehicles_to_check = [
        KickScooter(
            inventory_number=101,
            name="Ninebot Max Pro HSE",
            simplicity_rating=8,
            daily_energy_kwh=1.4,
            has_seat=False,
            is_technically_sound=True,
        ),
        KickScooter(
            inventory_number=102,
            name="Xiaomi Pro Покровский",
            simplicity_rating=9,
            daily_energy_kwh=1.1,
            has_seat=False,
            is_technically_sound=False,  # Неисправен — техосмотр должен отклонить!
        ),
        ElectricBike(
            inventory_number=103,
            name="Электровелосипед ВышКат Cruiser",
            simplicity_rating=5,  # Слишком сложный для новичка (< 6)
            daily_energy_kwh=2.6,
            max_assist_speed_kmh=25,
            is_technically_sound=True,
        ),
        MechanicalBike(
            inventory_number=104,
            name="Городской велосипед Шаболовка",
            simplicity_rating=7,
            gears_count=7,
            is_technically_sound=True,
        ),
    ]

    for v in vehicles_to_check:
        try_register_vehicle(fleet, v)

    # Демонстрация защиты от дубликата инвентарного номера
    duplicate_scooter = KickScooter(
        inventory_number=101,
        name="Дубликат самоката",
        simplicity_rating=6,
        daily_energy_kwh=1.0,
    )
    try_register_vehicle(fleet, duplicate_scooter)

    # Сценарий постановки на баланс инвентарных вещей
    print("\n2. ПОСТАНОВКА НА БАЛАНС ВЕЩЕЙ И ОБОРУДОВАНИЯ:")
    equipment_list = [
        Helmet(inventory_number=201, name="Защитный шлем ВышКат Safe", size="M"),
        Helmet(inventory_number=202, name="Защитный шлем ВышКат Safe", size="L"),
        ChargingStation(
            inventory_number=301,
            name="Зарядный шкаф Корпус R (Покровка)",
            daily_energy_kwh=14.5,
            ports_count=10,
        ),
    ]

    for eq in equipment_list:
        fleet.add_equipment(eq)
        print(f"  [Имущество] #{eq.inventory_number} «{eq.name}» -> ПОСТАВЛЕНО НА БАЛАНС")

    # Отчёт по всему имуществу на балансе (техника + вещи)
    print("\n3. РЕЕСТР ИМУЩЕСТВА НА БАЛАНСЕ (ИНВЕНТАРНАЯ ВЕДОМОСТЬ):")
    all_items = fleet.get_all_inventory()
    for item in all_items:
        energy_info = (
            f" | расход энергии: {item.daily_energy_kwh:.2f} кВт·ч/сут"
            if isinstance(item, IEnergyConsumer)
            else " | не потребляет электроэнергию"
        )
        print(f"  • Инв. №{item.inventory_number:<4} | {item.name}{energy_info}")

    # Сводный отчёт по численности и энергопотреблению
    print("\n4. СВОДКА ПО ЧИСЛЕННОСТИ И ЭНЕРГОПОТРЕБЛЕНИЮ ПАРКА:")
    print(f"  • Всего объектов на балансе:     {len(all_items)} ед.")
    print(f"  • Активных транспортных средств: {len(fleet.get_vehicles())} ед.")
    print(f"  • Единиц инвентарных вещей:      {len(fleet.get_equipment())} ед.")
    print(
        f"  • Суммарное потребление энергии: {fleet.get_total_daily_energy_kwh():.2f} кВт·ч/сутки"
    )

    # Список техники, доступной для новичков
    print("\n5. ТРАНСПОРТ, ДОПУЩЕННЫЙ ДЛЯ НОВИЧКОВ (простота >= 6):")
    for nv in fleet.get_novice_friendly_vehicles():
        print(
            f"  • Инв. №{nv.inventory_number:<4} | {nv.name} "
            f"(оценка простоты: {nv.simplicity_rating}/10)"
        )
    print("=" * 72)


if __name__ == "__main__":
    main()
