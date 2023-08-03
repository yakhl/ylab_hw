import uvicorn
from fastapi import FastAPI

from . import models
from .db import engine
from .routers import dish_router, menu_router, submenu_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(menu_router.router)
app.include_router(submenu_router.router)
app.include_router(dish_router.router)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
