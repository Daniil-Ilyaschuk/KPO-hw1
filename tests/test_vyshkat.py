from __future__ import annotations
import unittest
from unittest.mock import MagicMock

from domain.interfaces import IServiceCenter
from domain.vehicles import KickScooter, ElectricBike, MechanicalBike, Vehicle
from domain.equipment import Helmet, ChargingStation
from services.service_center import DefaultServiceCenter
from services.fleet_manager import FleetManager
from services.container import DIContainer


class AlwaysRejectServiceCenterStub(IServiceCenter):
    """Stub-реализация техосмотра, которая отклоняет любую технику"""

    def inspect(self, vehicle: Vehicle) -> bool:
        return False


class AlwaysApproveServiceCenterStub(IServiceCenter):
    """Stub-реализация техосмотра, которая принимает даже неисправную технику"""

    def inspect(self, vehicle: Vehicle) -> bool:
        return True


class TestVyshKatFleet(unittest.TestCase):
    """Юнит-тесты поведения парка «ВышКат» и DI-контейнера"""

    def setUp(self) -> None:
        self.container = DIContainer()
        self.container.register(IServiceCenter, DefaultServiceCenter)
        self.fleet = self.container.resolve(FleetManager)

    def test_accepts_sound_vehicle_and_rejects_faulty_one(self) -> None:
        """Техосмотр принимает исправный транспорт и отклоняет неисправный"""
        good_scooter = KickScooter(1, "Ninebot Good", simplicity_rating=8, daily_energy_kwh=1.2)
        broken_scooter = KickScooter(
            2, "Ninebot Broken", simplicity_rating=8, daily_energy_kwh=1.2, is_technically_sound=False
        )

        self.assertTrue(self.fleet.try_add_vehicle(good_scooter))
        self.assertFalse(self.fleet.try_add_vehicle(broken_scooter))
        self.assertEqual(len(self.fleet.get_vehicles()), 1)
        self.assertEqual(self.fleet.get_vehicles()[0].inventory_number, 1)

    def test_di_substitution_with_stub_service_center(self) -> None:
        """Проверка подмены техосмотра через DI-контейнер на Stub-реализацию"""
        # Подменяем зависимость в DI-контейнере на строгий Stub (всегда отказывает)
        self.container.register(IServiceCenter, AlwaysRejectServiceCenterStub)
        strict_fleet = self.container.resolve(FleetManager)

        ideal_scooter = KickScooter(10, "Ideal Scooter", simplicity_rating=9, daily_energy_kwh=1.0)
        self.assertFalse(strict_fleet.try_add_vehicle(ideal_scooter))
        self.assertEqual(len(strict_fleet.get_vehicles()), 0)

        # Подменяем зависимость на всеразрешающий Stub (принимает даже сломанный самокат)
        self.container.register(IServiceCenter, AlwaysApproveServiceCenterStub)
        lenient_fleet = self.container.resolve(FleetManager)

        broken_scooter = KickScooter(
            11, "Broken Scooter", simplicity_rating=7, daily_energy_kwh=1.0, is_technically_sound=False
        )
        self.assertTrue(lenient_fleet.try_add_vehicle(broken_scooter))
        self.assertEqual(len(lenient_fleet.get_vehicles()), 1)

    def test_di_substitution_with_magic_mock(self) -> None:
        """Проверка вызова метода inspect() через MagicMock, зарегистрированный в DI"""
        mock_inspector = MagicMock(spec=IServiceCenter)
        mock_inspector.inspect.return_value = True

        self.container.register_instance(IServiceCenter, mock_inspector)
        fleet_with_mock = self.container.resolve(FleetManager)

        bike = MechanicalBike(20, "Test Bike", simplicity_rating=7)
        accepted = fleet_with_mock.try_add_vehicle(bike)

        self.assertTrue(accepted)
        mock_inspector.inspect.assert_called_once_with(bike)

    def test_novice_friendly_vehicles_filtering(self) -> None:
        """Фильтрация для новичков отбирает только технику с простотой >= 6"""
        v_hard = ElectricBike(1, "Pro Bike", simplicity_rating=5, daily_energy_kwh=2.5)
        v_border = KickScooter(2, "Standard Scooter", simplicity_rating=6, daily_energy_kwh=1.2)
        v_easy = MechanicalBike(3, "Easy City Bike", simplicity_rating=9)

        self.fleet.try_add_vehicle(v_hard)
        self.fleet.try_add_vehicle(v_border)
        self.fleet.try_add_vehicle(v_easy)

        novice_vehicles = self.fleet.get_novice_friendly_vehicles()
        novice_ids = [v.inventory_number for v in novice_vehicles]

        self.assertEqual(novice_ids, [2, 3])

    def test_total_daily_energy_consumption_calculation(self) -> None:
        """Суммарная энергия учитывает электротранспорт и зарядные станции, игнорируя шлемы и мех. велосипеды."""
        self.fleet.try_add_vehicle(
            KickScooter(1, "Scooter", simplicity_rating=8, daily_energy_kwh=1.5)
        )
        self.fleet.try_add_vehicle(
            ElectricBike(2, "E-Bike", simplicity_rating=6, daily_energy_kwh=2.5)
        )
        self.fleet.try_add_vehicle(
            MechanicalBike(3, "Mech Bike", simplicity_rating=7)
        )
        self.fleet.add_equipment(Helmet(4, "Helmet", size="M"))
        self.fleet.add_equipment(
            ChargingStation(5, "Dock Station", daily_energy_kwh=10.0, ports_count=6)
        )

        self.assertAlmostEqual(self.fleet.get_total_daily_energy_kwh(), 14.0)
        self.assertEqual(len(self.fleet.get_all_inventory()), 5)
        self.assertEqual(len(self.fleet.get_equipment()), 2)

    def test_duplicate_inventory_number_raises_error(self) -> None:
        """Попытка добавить технику или вещь с существующим инвентарным номером вызывает ValueError"""
        self.fleet.add_equipment(Helmet(100, "First Item"))

        with self.assertRaises(ValueError):
            self.fleet.try_add_vehicle(MechanicalBike(100, "Duplicate Vehicle", simplicity_rating=8))

        with self.assertRaises(ValueError):
            self.fleet.add_equipment(Helmet(100, "Duplicate Equipment"))

    def test_domain_validation_errors(self) -> None:
        """Проверка валидации некорректных параметров при создании доменных объектов"""
        with self.assertRaises(ValueError):
            MechanicalBike(0, "Invalid ID", simplicity_rating=5)
        with self.assertRaises(ValueError):
            MechanicalBike(1, "Invalid Simplicity Low", simplicity_rating=0)
        with self.assertRaises(ValueError):
            MechanicalBike(1, "Invalid Simplicity High", simplicity_rating=11)
        with self.assertRaises(ValueError):
            KickScooter(1, "Negative Energy", simplicity_rating=5, daily_energy_kwh=-0.5)
        with self.assertRaises(ValueError):
            Helmet(-5, "Negative Equipment ID")
        with self.assertRaises(ValueError):
            ChargingStation(10, "Negative Station Energy", daily_energy_kwh=-1.0)


if __name__ == "__main__":
    unittest.main()
