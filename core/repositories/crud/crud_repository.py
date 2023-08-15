class CrudRepository:
    def __init__(self):
        self.menu_404_msg = 'menu not found'
        self.menu_409_title_msg = 'Another menu with this title already exists.'
        self.menu_409_id_msg = 'Another menu with this id already exists.'
        self.menu_200_deleted_msg = 'The menu has been deleted'

        self.submenu_404_msg = 'submenu not found'
        self.submenu_409_title_msg = 'Another submenu with this title already exists in the menu.'
        self.submenu_409_id_msg = 'Another submenu with this id already exists.'
        self.submenu_200_deleted_msg = 'The submenu has been deleted'

        self.dish_404_msg = 'dish not found'
        self.dish_409_title_msg = 'Another dish with this title already exists in the submenu.'
        self.dish_409_id_msg = 'Another dish with this id already exists.'
        self.dish_200_deleted_msg = 'The dish has been deleted'
