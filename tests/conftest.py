import asyncio

import pytest_asyncio
from httpx import AsyncClient

from core.main import app


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def client():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


class MenuValueStorage:
    id: None | str = None
    title: None | str = None
    description: None | str = None


class SubmenuValueStorage:
    id: None | str = None
    title: None | str = None
    description: None | str = None


class DishValueStorage:
    id: None | str = None
    title: None | str = None
    description: None | str = None
    price: float = 0
