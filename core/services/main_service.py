from uuid import UUID


class MainService:
    @staticmethod
    def get_all_submenus_id(menu_id: UUID | str, all_submenus_tag: str) -> str:
        return f'{menu_id}:{all_submenus_tag}'

    @staticmethod
    def get_all_dishes_id(menu_id: UUID | str, submenu_id: UUID | str, all_dishes_tag: str) -> str:
        return f'{menu_id}:{submenu_id}:{all_dishes_tag}'
