from pydantic import BaseModel

from core.repositories.crud.crud_repository import CrudRepository

crud_repo = CrudRepository()


class Menu404(BaseModel):
    message: str = crud_repo.menu_404_msg


class MenuTitle409(BaseModel):
    message: str = crud_repo.menu_409_title_msg


class MenuId409(BaseModel):
    message: str = crud_repo.menu_409_id_msg


class MenuDel200(BaseModel):
    status: bool = True
    message: str = crud_repo.menu_200_deleted_msg


class Submenu404(BaseModel):
    message: str = crud_repo.submenu_404_msg


class SubmenuTitle409(BaseModel):
    message: str = crud_repo.submenu_409_title_msg


class SubmenuId409(BaseModel):
    message: str = crud_repo.submenu_409_id_msg


class SubmenuDel200(BaseModel):
    message: str = crud_repo.submenu_200_deleted_msg


class Dish404(BaseModel):
    message: str = crud_repo.dish_404_msg


class DishTitle409(BaseModel):
    message: str = crud_repo.dish_409_title_msg


class DishId409(BaseModel):
    message: str = crud_repo.dish_409_id_msg


class DishDel200(BaseModel):
    message: str = crud_repo.dish_200_deleted_msg


class SyncTableSuccess200(BaseModel):
    status: bool = True
    message: str = 'success'


class SyncTableNoNeed200(BaseModel):
    status: bool = False
    message: str = 'no need to sync'
