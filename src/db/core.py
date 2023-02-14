from sqlalchemy import create_engine

from . import Base

__all__ = (
    'engine',
)

# engine = create_engine(
#     f"postgresql+psycopg2://root:root@127.0.0.1:5432/test_db"
# )
# Поскольку проект довольно простой, создаю engine мануально, без классов для обработки сессий
engine = create_engine(
    "sqlite:///example.db",
    connect_args={"check_same_thread": False},
)

Base.metadata.create_all(engine)
