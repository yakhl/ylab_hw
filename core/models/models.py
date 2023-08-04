from uuid import uuid4

from sqlalchemy import DECIMAL, UUID, Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from ..db import Base


class Menu(Base):
    __tablename__ = 'menus'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    submenus = relationship('Submenu', back_populates='menu', cascade='all, delete')


class Submenu(Base):
    __tablename__ = 'submenus'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id'), nullable=False, index=True)

    menu = relationship('Menu', back_populates='submenus')
    dishes = relationship('Dish', back_populates='submenu', cascade='all, delete')


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    price = Column(DECIMAL)
    submenu_id = Column(UUID(as_uuid=True), ForeignKey('submenus.id'), nullable=False, index=True)

    submenu = relationship('Submenu', back_populates='dishes')


Index('ix_submenus_menu_id_title', Submenu.menu_id, Submenu.title, unique=True)
Index('ix_dishes_submenu_id_title', Dish.submenu_id, Dish.title, unique=True)
