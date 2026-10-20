from __future__ import annotations
from domain.interfaces import IServiceCenter
from domain.vehicles import Vehicle


class DefaultServiceCenter(IServiceCenter):
    """Стандартная реализация сервиса техосмотра парка «ВышКат»"""

    def inspect(self, vehicle: Vehicle) -> bool:
        """
        Проверяет техническую исправность транспортного средства
        Устройство допускается в парк только если оно технически исправно
        """
        return vehicle.is_technically_sound
