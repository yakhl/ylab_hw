import uvicorn
from fastapi import FastAPI

from core.router import router
from core.db import engine
import core.models


core.models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
