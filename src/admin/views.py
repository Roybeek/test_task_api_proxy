from sqladmin import ModelView
from sqlalchemy import select, or_

from src.db import Station, Service, StationService, Fuel, StationFuel

__all__ = (
    'StationsView',
    'ServicesView',
    'StationServicesView',
    'FuelsView',
    'StationFuelsView',
)


class StationsView(ModelView, model=Station):
    column_list = [Station.external_id, Station.number, Station.address, Station.latitude, Station.longitude,
                   Station.created_at]
    column_searchable_list = [Station.address, Station.number]
    page_size = 50


class ServicesView(ModelView, model=Service):
    column_list = [Service.title, Service.title_for_user, Service.img_url, Service.created_at]
    column_searchable_list = [Service.title]
    page_size = 50


class StationServicesView(ModelView, model=StationService):
    column_list = [StationService.station, StationService.service]
    column_searchable_list = [StationService.station]
    page_size = 50

    def search_query(self, stmt, term):
        return stmt.join(Station, Station.external_id == StationService.station_id) \
            .where(or_(Station.number.like(f"%{term}%"), Station.address.like(f"%{term}%")))


class FuelsView(ModelView, model=Fuel):
    column_list = [Fuel.title, Fuel.title_for_user, Fuel.img_url, Fuel.created_at]


class StationFuelsView(ModelView, model=StationFuel):
    column_list = [StationFuel.station, StationFuel.fuel, StationFuel.cost, StationFuel.currency,
                   StationFuel.created_at]
    column_searchable_list = [StationFuel.station]
    page_size = 50

    def search_query(self, stmt, term):
        return stmt.join(Station, Station.external_id == StationFuel.station_id) \
            .filter(or_(Station.number.like(f"%{term}%"), Station.address.like(f"%{term}%")))
