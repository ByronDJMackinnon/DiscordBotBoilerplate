# db.py
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import Optional

class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self, url: str, echo: bool = False, pool_size: int = 5, max_overflow: int = 10):
        # asyncpg driver via SQLAlchemy's async URL
        self.url = url
        self.engine: Optional[AsyncEngine] = None
        self.sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    async def connect(self):
        if self.engine is None:
            self.engine = create_async_engine(
                self.url,
                echo=self.echo,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,
            )
            self.sessionmaker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def disconnect(self):
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.sessionmaker = None