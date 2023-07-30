import httpx
import os
from dotenv import load_dotenv


load_dotenv()

FASTAPI_HOST = os.environ.get("FASTAPI_HOST")

client = httpx.Client(base_url=f"http://{FASTAPI_HOST}:80")


class MenuValueStorage:
    id = None
    title = None
    description = None


class SubmenuValueStorage:
    id = None
    title = None
    description = None


class DishValueStorage:
    id = None
    title = None
    description = None
    price = None
