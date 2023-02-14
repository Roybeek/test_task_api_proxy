import uuid
from typing import List

from pydantic import BaseModel

__all__ = (
    'GasStationFuelData',
    'GasStationMainData',
    'FuelData',
    'GasStationUserValidData',
    'AdditionalServiceData'
)


class GasStationMainData(BaseModel):
    external_id: int
    number: str
    address: str
    latitude: float
    longitude: float
    img_list: List[str] = []
    additional_services: List[str] = []
    main_data_hash: str  # uuid.UUID


class FuelData(BaseModel):
    title: str
    cost: float
    currency: str
    img: str = ''


class GasStationFuelData(BaseModel):
    external_id: int
    fuel: List[FuelData]
    fuel_data_hash: str  # uuid.UUID


class AdditionalServiceData(BaseModel):
    title: str
    img: str = ''


class GasStationUserValidData(BaseModel):
    id: int
    number: str
    address: str
    latitude: float
    longitude: float
    additional_services: List[AdditionalServiceData] = []
    fuels: List[FuelData] = []
