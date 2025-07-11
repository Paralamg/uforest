from datetime import datetime
from typing import Annotated

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column

from config import get_settings

sync_engine = create_engine(
    url=get_settings().DATABASE_URL_psycopg,
    echo=False,
)

session_factory = sessionmaker(sync_engine)


def get_session():
    with session_factory() as session:
        yield session


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=text("CURRENT_TIMESTAMP"))]
updated_at = Annotated[datetime, mapped_column(
    server_default=text("CURRENT_TIMESTAMP"),
    onupdate=text("CURRENT_TIMESTAMP"),
)]


class Base(DeclarativeBase):
    pass


def init_database():
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
