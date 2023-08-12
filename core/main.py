import uvicorn
from fastapi import FastAPI

from .routers import dish_router, menu_router, submenu_router

app = FastAPI()

app.include_router(menu_router.router, prefix='/api/v1')
app.include_router(submenu_router.router, prefix='/api/v1/menus/{menu_id}')
app.include_router(dish_router.router, prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
