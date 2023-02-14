from sqlalchemy import Column, Integer, String, ForeignKey, Float, UUID
from sqlalchemy.orm import relationship

from src.db.models.base import Base

__all__ = (
    'Base',
    'Service',
    'StationService',
    'Fuel',
    'StationFuel'
)


class Service(Base):
    __tablename__ = "services"

    title = Column(String(), unique=True)
    title_for_user = Column(String())
    img_url = Column(String())

    def __str__(self) -> str:
        return f"{self.title}"


class StationService(Base):
    __tablename__ = "station_services"

    station_id = Column(Integer(), ForeignKey("stations.external_id"), nullable=False)
    service_id = Column(Integer(), ForeignKey("services.id"), nullable=False)

    station = relationship("Station", foreign_keys=[station_id])
    service = relationship("Service", foreign_keys=[service_id])


class Fuel(Base):
    __tablename__ = "fuels"

    title = Column(String(), unique=True)
    title_for_user = Column(String())

    img_url = Column(String())

    def __str__(self) -> str:
        return f"{self.title}"


class StationFuel(Base):
    __tablename__ = "station_fuels"

    station_id = Column(String(), ForeignKey("stations.external_id"), nullable=False)
    fuel_id = Column(String(), ForeignKey("fuels.id"), nullable=False)
    cost = Column(Float())
    currency = Column(String(25))

    station = relationship("Station", foreign_keys=[station_id])
    fuel = relationship("Fuel", foreign_keys=[fuel_id])


class Image(Base):
    __tablename__ = "images"

    station_id = Column(String(), ForeignKey("stations.id"), nullable=False)
    url = Column(String(), unique=True)
