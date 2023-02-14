import logging

from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import Session

from src.db import engine, Station, StationService, Service, Fuel, StationFuel
from src.schemas import GasStationMainData, GasStationFuelData, FuelData

__all__ = (
    'GasStationRepository'
)

LOGGER = logging.getLogger('main')


class GasStationRepository:
    """
    Интерфейс для работы с данными в БД
    """

    @staticmethod
    async def get_all_hash() -> tuple:
        """
        Возвращает список станций с хешем.
        :return: Список всех станций с id и хешем для 1 и 2 источника.
        """
        with engine.connect() as connection:
            res = connection.execute(
                select(Station.external_id, Station.main_data_hash))
            return res.fetchall()

    @staticmethod
    async def get_excluded_hash_stations(stations_fuel_hash_list: list) -> tuple:
        """
        Возвращает те станции, хешей которых нет в списке.
        :param stations_fuel_hash_list:
        :return: кортеж из списков с id и hash ([Station.external_id, Station.fuel_data_hash],)
        """
        with engine.connect() as connection:
            with Session(bind=connection) as session:
                res = connection.execute(
                    select(
                        Station.external_id,
                        Station.fuel_data_hash
                    ).where(
                        Station.external_id.not_in(
                            select(Station.external_id).where(Station.fuel_data_hash.in_(stations_fuel_hash_list))
                        )
                    )
                )
                return res.fetchall()

    @staticmethod
    async def update_station_info(_station: GasStationMainData) -> None:
        """
        Обновить данные о станции.
        :param _station: модель GasStationMainData с данными о станции.
        """
        with engine.connect() as connection:
            with Session(bind=connection) as session:
                stmt = update(Station) \
                    .where(Station.external_id == _station.external_id) \
                    .values(number=_station.number,
                            address=_station.address,
                            latitude=_station.latitude,
                            longitude=_station.longitude,
                            main_data_hash=_station.main_data_hash)
                session.execute(stmt)
                session.commit()

    @staticmethod
    async def get_station_service_info(station_id: int) -> tuple:
        """
        Получить список услуг для станций в бд.
        :param station_id: id станции из источника.
        :return: Кортеж с списком из Service.id и Service.title
        """
        with engine.connect() as connection:
            res = connection.execute(
                select(
                    Service.id,
                    Service.title
                ).join(
                    StationService,
                    Service.id == StationService.service_id).where(StationService.station_id == station_id)
            )
            return res.fetchall()

    @staticmethod
    async def add_service_for_station(station_id: int, service_title: str) -> None:
        """
        Добавить услугу для станции.
        :param station_id: id станции из источника
        :param service_title: title для услуги
        """
        try:
            LOGGER.info(f"Добавление нового типа услуги - {service_title} для станции {station_id}")
            with engine.connect() as connection:
                with Session(bind=connection) as session:
                    res = session.execute(
                        select(Service.id).where(Service.title == service_title)
                    )
                    rows = res.fetchall()
                    if not rows:
                        stmt = insert(Service).values(title=service_title, title_for_user=service_title)
                        # sqlite не поддерживает returning, поэтому придется еще раз запросить
                        session.execute(stmt)
                        session.commit()
                        new_res = session.execute(
                            select(Service.id).where(Service.title == service_title)
                        )
                        service_id = new_res.fetchall()[0][0]
                    else:
                        service_id = rows[0][0]
                    session.execute(
                        insert(StationService).values(station_id=station_id, service_id=service_id)
                    )
                    session.commit()
        except Exception as e:
            LOGGER.error(f"Ошибка при обновлении услуги - {e}")

    @staticmethod
    async def remove_service_for_station(station_id: int, service_id: int) -> None:
        """
        Удалить услугу у станции.
        :param station_id: external id станции
        :param service_id: id услуги
        """
        LOGGER.info(f"Удаление услуги с id {service_id} для станции {station_id}")
        with engine.connect() as connection:
            with Session(bind=connection) as session:
                stmt = delete(StationService).where(StationService.station_id == station_id,
                                                    StationService.service_id == service_id)
                session.execute(stmt)
                session.commit()

    @staticmethod
    async def get_station_fuels(station_id: int) -> tuple:
        """
        Получить список топлива для станций в бд.
        :param station_id: id станции из источника.
        :return: Кортеж с списком из Fuel.id, Fuel.title, Fuel.cost, Fuel.currency
        """
        with engine.connect() as connection:
            res = connection.execute(
                select(
                    Fuel.id,
                    Fuel.title,
                    StationFuel.cost,
                    StationFuel.currency
                ).join(
                    StationFuel,
                    Fuel.id == StationFuel.fuel_id
                ).where(StationFuel.station_id == station_id)
            )
            return res.fetchall()

    @staticmethod
    async def update_fuel_cost(station_id: int, fuel_id: int, fuel_cost: float, fuel_currency: str) -> None:
        """
        Обновить значение стоимости для топлива в БД
        :param station_id: external_id станции
        :param fuel_id: id топлива
        :param fuel_cost: стоимость
        :param fuel_currency: валюта
        :return:
        """
        LOGGER.info(f"Обновление стоимости топлива с id {fuel_id} для станции {station_id}")
        with engine.connect() as connection:
            with Session(bind=connection) as session:
                stmt = update(StationFuel) \
                    .where(StationFuel.fuel_id == fuel_id, StationFuel.station_id == station_id) \
                    .values(cost=fuel_cost,
                            currency=fuel_currency)
                session.execute(stmt)
                session.commit()

    @staticmethod
    async def add_fuel_for_station(station_id: int, _fuel: FuelData) -> None:
        """
        Добавить топливо для станции.
        :param station_id: id станции из источника
        :param _fuel: модель FuelData
        """
        try:
            LOGGER.info(f"Обновление топлива - {_fuel} для станции {station_id}")
            with engine.connect() as connection:
                with Session(bind=connection) as session:
                    res = session.execute(
                        select(Fuel.id).where(Fuel.title == _fuel.title)
                    )
                    rows = res.fetchall()
                    if not rows:
                        stmt = insert(Fuel).values(
                            title=_fuel.title,
                            title_for_user=_fuel.title
                        )

                        # sqlite не поддерживает returning, поэтому придется еще раз запросить
                        connection.execute(stmt)
                        connection.commit()
                        new_res = session.execute(
                            select(Fuel.id).where(Fuel.title == _fuel.title)
                        )
                        fuel_id = new_res.fetchall()[0][0]
                    else:
                        fuel_id = rows[0][0]
                    session.execute(
                        insert(StationFuel).values(station_id=station_id,
                                                   fuel_id=fuel_id,
                                                   cost=_fuel.cost,
                                                   currency=_fuel.currency)
                    )
                    session.commit()

        except Exception as e:
            LOGGER.error(f"Ошибка при обновлении информации о топливе - {e}")

    @staticmethod
    async def remove_fuel_for_station(station_id: int, fuel_id: int) -> None:
        """
        Удалить услугу у станции.
        :param station_id: id станции
        :param fuel_id: id топлива
        """
        LOGGER.info(f"Удаление информации о топливе с id {fuel_id} для станции {station_id}")
        with engine.connect() as connection:
            with Session(bind=connection) as session:
                stmt = delete(StationFuel).where(StationFuel.station_id == station_id,
                                                 StationFuel.fuel_id == fuel_id)
                session.execute(stmt)
                session.commit()

    @staticmethod
    async def update_station_fuel_hash_data(station_id: int, hash_data: str) -> None:
        """
        Обновить fuel_data_hash для станции
        :param station_id:
        :param hash_data:
        :return:
        """
        with engine.connect() as connection:
            with Session(bind=connection) as session:
                stmt = update(Station) \
                    .where(Station.external_id == station_id) \
                    .values(fuel_data_hash=hash_data)
                session.execute(stmt)
                session.commit()

    @staticmethod
    async def create_station(_station: GasStationMainData) -> None:
        """
        Создать объект станции в БД.
        :param _station: Модель GasStationMainData
        """
        LOGGER.info(f"Создание записи для станции - {_station}")
        with engine.connect() as connection:
            with Session(bind=connection) as session:
                stmt = insert(Station).values(
                    external_id=_station.external_id,
                    number=_station.number,
                    address=_station.address,
                    latitude=_station.latitude,
                    longitude=_station.longitude,
                    main_data_hash=_station.main_data_hash)
                session.execute(stmt)
                session.commit()

    @staticmethod
    async def get_all_stations() -> tuple:
        """
        Получить все станции из бд.
        :return: Кортеж с external_id, number, address, longitude, latitude
        """
        with engine.connect() as connection:
            res = connection.execute(
                select(Station.external_id,
                       Station.number,
                       Station.address,
                       Station.longitude,
                       Station.latitude)
            )
            return res.fetchall()

    @staticmethod
    async def get_station_service_for_users(station_id: int) -> tuple:
        """
        Получить список услуг для станций в бд.
        :param station_id: id станции из источника.
        :return: Кортеж с списком из Service.id, Service.title_for_user, Service.img_url
        """
        with engine.connect() as connection:
            res = connection.execute(
                select(
                    Service.id,
                    Service.title_for_user,
                    Service.img_url
                ).join(
                    StationService,
                    Service.id == StationService.service_id).where(StationService.station_id == station_id)
            )
            return res.fetchall()

    @staticmethod
    async def get_station_fuels_for_user(station_id: int) -> tuple:
        """
        Получить список топлива для станций в бд.
        :param station_id: id станции из источника.
        :return: Кортеж с списком из Fuel.id, Fuel.title_for_user, Fuel.cost, Fuel.currency, Fuel.img_url
        """
        with engine.connect() as connection:
            res = connection.execute(
                select(
                    Fuel.id,
                    Fuel.title_for_user,
                    StationFuel.cost,
                    StationFuel.currency,
                    Fuel.img_url
                ).join(
                    StationFuel,
                    Fuel.id == StationFuel.fuel_id
                ).where(StationFuel.station_id == station_id)
            )
            return res.fetchall()

    @staticmethod
    async def get_station(station_id: int) -> tuple:
        """
        Получить все станции из бд.
        :param station_id: id станции из источника.
        :return: Кортеж с external_id, number, address, longitude, latitude
        """
        with engine.connect() as connection:
            res = connection.execute(
                select(
                    Station.external_id,
                    Station.number,
                    Station.address,
                    Station.longitude,
                    Station.latitude
                ).where(Station.external_id == station_id)
            )
            return res.fetchall()
