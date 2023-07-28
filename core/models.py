from sqlalchemy import Column, ForeignKey, String, DECIMAL, UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from .db import Base


class Menu(Base):
    __tablename__ = "menus"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, unique=True)
    description = Column(String)

    submenus = relationship("Submenu", back_populates="menu", cascade="all, delete")


class Submenu(Base):
    __tablename__ = "submenus"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String)
    description = Column(String)
    menu_id = Column(UUID, ForeignKey("menus.id"))

    menu = relationship("Menu", back_populates="submenus")
    dishes = relationship("Dish", back_populates="submenu", cascade="all, delete")


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String)
    description = Column(String)
    price = Column(DECIMAL)
    submenu_id = Column(UUID, ForeignKey("submenus.id"))

    submenu = relationship("Submenu", back_populates="dishes")
