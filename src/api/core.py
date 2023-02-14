import logging

from fastapi import FastAPI
from starlette.responses import JSONResponse

from src.admin import AdminManager
from src.db import engine
from src.helpers import ApiAnswer, BadRequest
from src.modules import SourceHandler, Stations
from src.schedule import schedule

app = FastAPI()

admin = AdminManager(app, engine)

admin.reg_views()

LOGGER = logging.getLogger('main')


@app.on_event("startup")
async def startup():
    LOGGER.info('START APP')
    source_handler = SourceHandler()
    try:
        await source_handler.check_source_1_for_updates()
        await source_handler.check_source_2_for_updates()
    except BadRequest as e:
        LOGGER.error(str(e))

    schedule(source_handler)


@app.get("/get_all_stations_info", tags=["stations"])
async def get_all_stations_info():
    """
    Получить список всех станций из объединенных источников.
    """
    data = await Stations.get_all_stations_info()
    return ApiAnswer.response(data=data)


@app.get("/get_station_info", tags=["stations"])
async def get_station_info(station_id: int):
    """
    Получить данные о станции по его id.
    """
    data = await Stations.get_station_info(station_id)
    return ApiAnswer.response(data=data)
