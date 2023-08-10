from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)


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
