import os
from uuid import UUID

import pandas as pd
from fastapi import Depends, HTTPException

from core.schemas.dish_schemas import DishCreateSchema, DishUpdateSchema
from core.schemas.menu_schemas import MenuCreateSchema, MenuUpdateSchema
from core.schemas.submenu_schemas import SubmenuCreateSchema, SubmenuUpdateSchema
from core.services.dish_service import DishService
from core.services.menu_service import MenuService
from core.services.submenu_service import SubmenuService


class TableSync:
    xlsx_path = os.path.join('core', 'admin', 'Menu.xlsx')
    last_update_time = 0.0

    def __init__(
        self, menu: MenuService = Depends(), submenu: SubmenuService = Depends(), dish: DishService = Depends()
    ):
        self.data = pd.read_excel(self.xlsx_path, header=None, dtype=str)
        self.menu = menu
        self.submenu = submenu
        self.dish = dish

    async def _delete_dishes(self, menu_id: UUID, submenu_id: UUID, table_dishes_ids: set) -> None:
        db_dishes_ids = await self.dish.get_all_ids(submenu_id)
        dishes_ids_to_delete = set(db_dishes_ids) - table_dishes_ids
        for dish_id_to_delete in dishes_ids_to_delete:
            await self.dish.delete(menu_id, submenu_id, dish_id_to_delete)

    async def _delete_submenus(self, menu_id: UUID, table_submenus_ids: set) -> None:
        db_submenus_ids = await self.submenu.get_all_ids(menu_id)
        submenus_ids_to_delete = set(db_submenus_ids) - table_submenus_ids
        for submenu_id_to_delete in submenus_ids_to_delete:
            await self.submenu.delete(menu_id, submenu_id_to_delete)

    async def _delete_menus(self, table_menus_ids: set) -> None:
        db_menus_ids = await self.menu.get_all_ids()
        menus_ids_to_delete = set(db_menus_ids) - table_menus_ids
        for menu_id_to_delete in menus_ids_to_delete:
            await self.menu.delete(menu_id_to_delete)

    async def sync_table(self) -> dict:
        current_update_time = os.path.getmtime(self.xlsx_path)
        if TableSync.last_update_time == current_update_time:
            return {'status': False, 'message': 'no need to sync'}
        table_menus_ids: set[UUID] = set()
        table_submenus_ids: set[UUID] = set()
        table_dishes_ids: set[UUID] = set()
        zero_uuid = UUID('00000000-0000-0000-0000-000000000000')
        menu_id = zero_uuid
        submenu_id = zero_uuid
        dish_id = zero_uuid

        for _, row in self.data.iterrows():
            if not pd.isna(row[0]):
                await self._delete_submenus(menu_id, table_submenus_ids)
                table_submenus_ids = set()
                menu_id, menu_title, menu_description = UUID(row[0]), row[1], row[2]
                table_menus_ids.add(menu_id)
                menu_data = {'title': menu_title, 'description': menu_description}
                try:
                    await self.menu.update(menu_id, MenuUpdateSchema(**menu_data))
                except HTTPException as exc:
                    if exc.status_code == 404:
                        await self.menu.create(MenuCreateSchema(id=menu_id, **menu_data))
                    else:
                        raise
                continue

            if not pd.isna(row[1]):
                await self._delete_dishes(menu_id, submenu_id, table_dishes_ids)
                table_dishes_ids = set()
                submenu_id, submenu_title, submenu_description = UUID(row[1]), row[2], row[3]
                table_submenus_ids.add(submenu_id)
                submenu_data = {'title': submenu_title, 'description': submenu_description}
                try:
                    await self.submenu.update(menu_id, submenu_id, SubmenuUpdateSchema(**submenu_data))
                except HTTPException as exc:
                    if exc.status_code == 404:
                        await self.submenu.create(menu_id, SubmenuCreateSchema(id=submenu_id, **submenu_data))
                    else:
                        raise
                continue

            if not pd.isna(row[2]):
                dish_id, dish_title = UUID(row[2]), row[3]
                dish_description, dish_price = row[4], row[5]
                table_dishes_ids.add(dish_id)
                dish_data = {'title': dish_title, 'description': dish_description, 'price': dish_price}
                try:
                    await self.dish.update(menu_id, submenu_id, dish_id, DishUpdateSchema(**dish_data))
                except HTTPException as exc:
                    if exc.status_code == 404:
                        await self.dish.create(menu_id, submenu_id, DishCreateSchema(id=dish_id, **dish_data))
                    else:
                        raise
                continue

        await self._delete_menus(table_menus_ids)
        await self._delete_submenus(menu_id, table_submenus_ids)
        await self._delete_dishes(menu_id, submenu_id, table_dishes_ids)
        TableSync.last_update_time = current_update_time
        return {'status': True, 'message': 'success'}
