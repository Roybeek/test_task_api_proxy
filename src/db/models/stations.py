from sqlalchemy import Column, Integer, String, ForeignKey, Float, UUID
from sqlalchemy.orm import relationship

from src.db.models.base import Base

__all__ = (
    'Base',
    'Station',
)


class Station(Base):
    __tablename__ = "stations"

    external_id = Column(Integer(), unique=True, nullable=False)
    number = Column(String(15))
    address = Column(String(255))
    latitude = Column(Float())
    longitude = Column(Float())
    main_data_hash = Column(String())  # UUID()
    fuel_data_hash = Column(String())  # UUID()

    def __str__(self) -> str:
        return f"{self.number} - {self.address}"
