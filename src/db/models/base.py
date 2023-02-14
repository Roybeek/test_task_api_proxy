from sqlalchemy import Column, Integer, String, create_engine, DateTime, func, MetaData
from sqlalchemy.ext.declarative import as_declarative, declarative_base
from datetime import datetime

__all__ = (
    'Base',
)


@as_declarative()
class Base(object):
    """
    Базовый класс таблицы от которого должны наследоваться остальные таблицы.

    Добавляет колонки:
     - id: Идентификатор
     - created_at: Дата/время создания записи
    """
    id = Column(Integer(), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now())
