import logging
import uuid
from typing import Dict

from src.modules.repositories import GasStationRepository
from src.schemas import GasStationMainData, GasStationFuelData, FuelData

__all__ = (
    'DataHandler'
)

LOGGER = logging.getLogger('main')


class DataHandler:

    @classmethod
    async def update_source_1_data(cls, stations: list) -> None:
        """
        Обновить данные в БД для 1 источника.
        :param stations: список станций из источника 1
        """
        # Переводим исходные данные в отсортированный словарь, чтобы была возможность получать данные по ключу (id)
        # А также формируем некоторый хеш
        station_dict = await cls.__get_main_data_dict_hash(stations)
        all_stations = await GasStationRepository.get_all_hash()
        # Проходимся по всем станциям, которые есть в БД, и если хеши отличаются, обновляем данные для станции
        for station in all_stations:
            if station_dict.get(station[0]):
                if station_dict.get(station[0]).main_data_hash != station[1]:
                    await GasStationRepository.update_station_info(station_dict.get(station[0]))
                    await cls.__update_station_services(station[0], station_dict.get(station[0]).additional_services)
                station_dict.pop(station[0])
        # Проходимся по станциям, которые остались в словаре. Значит их нет в базе, и требуется их создать
        for station_id in station_dict:
            await GasStationRepository.create_station(station_dict.get(station_id))
            await cls.__update_station_services(station_id, station_dict.get(station_id).additional_services)

    @classmethod
    async def update_source_2_data(cls, stations: list) -> None:
        """
        Обновить данные в БД для 2 источника.
        :param stations: Список станций из источника 2
        """
        # Переводим исходные данные в отсортированный словарь, чтобы была возможность получать данные по ключу (id)
        # На основе полученных хешей, получаем только отличные данные из бд
        station_dict = await cls.__get_fuel_data_dict_hash(stations)

        update_stations = await GasStationRepository.get_excluded_hash_stations(
            [station_dict.get(station_id).fuel_data_hash for station_id in station_dict])
        # Проходимся только по тем станциям, хеш которых отличается от источника
        for station in update_stations:
            if station_dict.get(station[0]):
                if station_dict.get(station[0]).fuel_data_hash != station[1]:
                    await cls.__update_station_fuel_info(station_dict.get(station[0]))
                    await GasStationRepository.update_station_fuel_hash_data(station[0], station_dict.get(
                        station[0]).fuel_data_hash)

    @staticmethod
    async def __get_main_data_dict_hash(data: list) -> Dict:
        """
        Получить словарь из списка станций, и получить хеш его данных.
        :param data: Список станций.
        :return: Модель GasStationMainData с ключами из id станций.
        """
        hash_dict = dict()
        for station in data:
            hash_dict.update({
                station["id"]: GasStationMainData(
                    external_id=station["id"],
                    number=station["number"],
                    address=station["address"],
                    latitude=station["latitude"],
                    longitude=station["longitude"],
                    img_list=station["img_list"],
                    additional_services=station["additional_services"],
                    main_data_hash=str(uuid.uuid3(uuid.NAMESPACE_DNS, station.__str__()))
                )
            })
        return hash_dict

    @staticmethod
    async def __get_fuel_data_dict_hash(data: list) -> Dict:
        """
        Получить словарь из списка станций, и получить хеш его данных.
        :param data: Список станций.
        :return: Модель GasStationFuelData с ключами из id станций.
        """
        hash_dict = dict()
        for station in data:
            hash_dict.update({
                station["id"]: GasStationFuelData(
                    external_id=station["id"],
                    fuel=[FuelData(**fuel) for fuel in station["fuel"]],
                    fuel_data_hash=str(uuid.uuid3(uuid.NAMESPACE_DNS, station.__str__()))
                )
            })
        return hash_dict

    @staticmethod
    async def __update_station_services(station_id: int, service_list: list) -> None:
        """
        Обновить список услуг для станции.
        :param station_id: id обновляемой станции
        :param service_list: Список дополнительных услуг для станции из источника.
        """
        internal_service_list = await GasStationRepository.get_station_service_info(station_id)
        internal_service_dict = {row[1]: row[0] for row in internal_service_list}  # {title: service_id}
        while service_list:
            service = service_list.pop()
            if internal_service_dict.get(service):
                # Услуга уже есть у станции
                internal_service_dict.pop(service)
            else:
                # Если в словаре нет услуги, значит требуется добавить его для станции
                await GasStationRepository.add_service_for_station(station_id, service)
        # Если в словаре остались услуги, значит их теперь нет в источнике, удалим их для станции
        for service_title in internal_service_dict:
            await GasStationRepository.remove_service_for_station(station_id,
                                                                  internal_service_dict.get(service_title))

    @staticmethod
    async def __update_station_fuel_info(source_station: GasStationFuelData):
        fuel_list = source_station.fuel
        internal_fuel_list = await GasStationRepository.get_station_fuels(source_station.external_id)
        internal_fuel_dict = {row[1]: row for row in internal_fuel_list}  # {title: Fuel}
        while fuel_list:
            fuel = fuel_list.pop()
            internal_fuel = internal_fuel_dict.get(fuel.title)
            if internal_fuel:
                # Топливо уже есть у станции
                # проверяем значения стоимости
                if internal_fuel[2] != fuel.cost and internal_fuel[3] != fuel.currency:
                    await GasStationRepository.update_fuel_cost(source_station.external_id,
                                                                internal_fuel[0],
                                                                fuel.cost,
                                                                fuel.currency)
                internal_fuel_dict.pop(fuel.title)
            else:
                # Если в словаре нет топлива, значит требуется добавить его для станции
                await GasStationRepository.add_fuel_for_station(source_station.external_id, fuel)
        # Если в словаре осталось топливо, значит их теперь нет в источнике, удалим их для станции в бд
        for fuel_title in internal_fuel_dict:
            await GasStationRepository.remove_fuel_for_station(source_station.external_id,
                                                               internal_fuel_dict.get(fuel_title)[0])
