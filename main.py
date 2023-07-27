import uvicorn
from fastapi import FastAPI

from router import router
from db import engine
import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
