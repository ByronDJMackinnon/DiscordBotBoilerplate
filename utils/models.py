# models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String
from .database import Base

class User(Base):
    __tablename__ = "users"
    discord_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)   # Discord user id
    name: Mapped[str] = mapped_column(String(64))
