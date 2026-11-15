"""
SQLAlchemy declarative base definition.
"""
from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Automatically generates table names based on class name.
    """
    id: Any
    __name__: str

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generates table name automatically.
        Example: UserModel -> user_model
        """
        return cls.__name__.lower()
