from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///./app.db'


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
