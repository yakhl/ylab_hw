import uvicorn
from fastapi import FastAPI

from core.routers import (
    admin_router,
    dish_router,
    full_menu_router,
    menu_router,
    submenu_router,
)

app = FastAPI()

app.include_router(full_menu_router.router, prefix='/api/v1')
app.include_router(menu_router.router, prefix='/api/v1')
app.include_router(submenu_router.router, prefix='/api/v1/menus/{menu_id}')
app.include_router(dish_router.router, prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}')
app.include_router(admin_router.router, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
