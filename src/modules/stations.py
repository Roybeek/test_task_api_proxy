from typing import List

from src.modules.repositories import GasStationRepository
from src.schemas import GasStationUserValidData, FuelData, AdditionalServiceData

__all__ = (
    'Stations'
)


class Stations:

    @staticmethod
    async def get_all_stations_info() -> List[dict]:
        """
        Получить объединенный список с данными от 1 и 2 источника.
        :return: Список с моделями GasStationUserValidData
        """
        stations_list = []
        stations = await GasStationRepository.get_all_stations()
        for station in stations:
            station_fuels = await GasStationRepository.get_station_fuels_for_user(station[0])
            station_services = await GasStationRepository.get_station_service_for_users(station[0])
            stations_list.append(
                GasStationUserValidData(
                    id=station[0],
                    number=station[1],
                    address=station[2],
                    latitude=station[3],
                    longitude=station[4],
                    additional_services=[AdditionalServiceData(title=service[1], img=service[2] if service[2] else '')
                                         for service in
                                         station_services],
                    fuels=[FuelData(title=_fuel[1], cost=_fuel[2], currency=_fuel[3], img=_fuel[4] if _fuel[4] else '')
                           for _fuel in
                           station_fuels]
                ).dict()
            )
        return stations_list

    @staticmethod
    async def get_station_info(station_id: int) -> dict:
        """
        Получить данные о конкретной станции
        :param station_id: external_id для станции
        :return: Данные о станции в модели GasStationUserValidData
        """
        station = (await GasStationRepository.get_station(station_id))[0]
        station_fuels = await GasStationRepository.get_station_fuels_for_user(station[0])
        station_services = await GasStationRepository.get_station_service_for_users(station[0])
        station_valid_data = GasStationUserValidData(
            id=station[0],
            number=station[1],
            address=station[2],
            latitude=station[3],
            longitude=station[4],
            additional_services=[AdditionalServiceData(title=service[1], img=service[2] if service[2] else '')
                                 for service in
                                 station_services],
            fuels=[FuelData(title=_fuel[1], cost=_fuel[2], currency=_fuel[3], img=_fuel[4] if _fuel[4] else '')
                   for _fuel in
                   station_fuels]
        )
        return station_valid_data.dict()
