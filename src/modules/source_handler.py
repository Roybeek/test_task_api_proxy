import logging
import time
import uuid

import aiohttp
from datetime import datetime

from src.helpers import singleton, BadRequest
from src.modules import DataHandler
from src.settings import SOURCE_1_URL, SOURCE_2_URL

LOGGER = logging.getLogger('main')


@singleton
class SourceHandler:

    def __init__(self):
        self.source_1_url: str = SOURCE_1_URL
        self.source_2_url: str = SOURCE_2_URL
        self.last_gas_station_info_update_time: datetime = datetime.now()
        self.last_fuel_info_update_time: datetime = datetime.now()
        self.gas_station_info_hash: str = str(uuid.uuid1())  # uuid.UUID
        self.fuel_info_hash: str = str(uuid.uuid1())  # uuid.UUID

    @staticmethod
    async def __request(url: str) -> aiohttp.ClientResponse:
        """
        Получить данные от источника по его url
        :param url: путь к источнику
        :return: response aiohttp.ClientResponse
        """
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    LOGGER.info(
                        f"url: {url} [get] [{response.status}] {(time.time() - start_time):.2f}s "
                    )
                    text = await response.text()
                    return response
        except Exception as e:
            raise BadRequest(msg=f"Ошибка получения данных от {url} - {e}")

    async def check_source_1_for_updates(self):
        response = await self.__request(self.source_1_url)
        if response.status == 200:
            data = await response.json()
            if data["status"] == "ok":
                new_hash = str(uuid.uuid3(uuid.NAMESPACE_DNS, await response.text()))
                if new_hash != self.gas_station_info_hash:
                    LOGGER.info(f"Проверка локальных данных от 1 источника")
                    await DataHandler.update_source_1_data(data["data"])
                    self.gas_station_info_hash = new_hash
                    return True
                else:
                    return False
        else:
            raise BadRequest(msg=str(await response.json()) if await response.json() else {
                "result": f"Ошибка выполнения запроса без ответа от сервиса"}, status_code=response.status)

    async def check_source_2_for_updates(self):
        response = await self.__request(self.source_2_url)

        if response.status == 200:
            data = await response.json()
            if data["status"] == "ok":
                new_hash = str(uuid.uuid3(uuid.NAMESPACE_DNS, await response.text()))
                if new_hash != self.fuel_info_hash:
                    LOGGER.info(f"Проверка локальных данных от 2 источника")
                    await DataHandler.update_source_2_data(data["data"])
                    self.fuel_info_hash = new_hash
                    return True
                else:
                    return False
        else:
            raise BadRequest(msg=str(await response.json()) if await response.json() else {
                "result": f"Ошибка выполнения запроса без ответа от сервиса"}, status_code=response.status)
