import httpx
import os
from dotenv import load_dotenv


load_dotenv()

FASTAPI_HOST = os.environ.get("FASTAPI_HOST", "localhost")
FASTAPI_PORT = os.environ.get("FASTAPI_PORT", "8000")

client = httpx.Client(base_url=f"http://{FASTAPI_HOST}:{FASTAPI_PORT}")


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
