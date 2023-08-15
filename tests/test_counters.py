import pytest
from httpx import AsyncClient

from tests.conftest import DishValueStorage, MenuValueStorage, SubmenuValueStorage


class TestCounters:
    @pytest.mark.asyncio
    async def test_create_menu(self, client: AsyncClient):
        MenuValueStorage.title = 'Menu title 1'
        MenuValueStorage.description = 'Menu description 1'
        response = await client.post(
            '/api/v1/menus',
            json={
                'title': MenuValueStorage.title,
                'description': MenuValueStorage.description,
            },
        )
        assert response.status_code == 201, response.text
        data_out = response.json()
        MenuValueStorage.id = data_out['id']

    @pytest.mark.asyncio
    async def test_create_submenu(self, client: AsyncClient):
        SubmenuValueStorage.title = 'Submenu title 1'
        SubmenuValueStorage.description = 'Submenu description 1'
        response = await client.post(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus',
            json={
                'title': SubmenuValueStorage.title,
                'description': SubmenuValueStorage.description,
            },
        )
        assert response.status_code == 201, response.text
        data_out = response.json()
        SubmenuValueStorage.id = data_out['id']

    @pytest.mark.asyncio
    async def test_create_dish1(self, client: AsyncClient):
        DishValueStorage.title1 = 'Dish title 1'
        DishValueStorage.description1 = 'Dish description 1'
        DishValueStorage.price1 = 12.5345
        response = await client.post(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes',
            json={
                'title': DishValueStorage.title1,
                'description': DishValueStorage.description1,
                'price': DishValueStorage.price1,
            },
        )
        assert response.status_code == 201, response.text
        data_out = response.json()
        DishValueStorage.id1 = data_out['id']

    @pytest.mark.asyncio
    async def test_create_dish2(self, client: AsyncClient):
        DishValueStorage.title2 = 'Dish title 2'
        DishValueStorage.description2 = 'Dish description 2'
        DishValueStorage.price2 = 56.1245
        response = await client.post(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes',
            json={
                'title': DishValueStorage.title2,
                'description': DishValueStorage.description2,
                'price': DishValueStorage.price2,
            },
        )
        assert response.status_code == 201, response.text
        data_out = response.json()
        DishValueStorage.id2 = data_out['id']

    @pytest.mark.asyncio
    async def test_read_menu_after_create(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}')
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert data_out == {
            'id': MenuValueStorage.id,
            'title': MenuValueStorage.title,
            'description': MenuValueStorage.description,
            'submenus_count': 1,
            'dishes_count': 2,
        }

    @pytest.mark.asyncio
    async def test_read_submenu_after_create(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}')
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert data_out == {
            'id': SubmenuValueStorage.id,
            'title': SubmenuValueStorage.title,
            'description': SubmenuValueStorage.description,
            'menu_id': MenuValueStorage.id,
            'dishes_count': 2,
        }

    @pytest.mark.asyncio
    async def test_delete_submenu(self, client: AsyncClient):
        response = await client.delete(f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}')
        assert response.status_code == 200, response.text

    @pytest.mark.asyncio
    async def test_read_submenus_after_delete(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}/submenus')
        assert response.status_code == 200, response.text
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_read_dishes_after_delete(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes')
        assert response.status_code == 200, response.text
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_read_menu_after_delete(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}')
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert data_out == {
            'id': MenuValueStorage.id,
            'title': MenuValueStorage.title,
            'description': MenuValueStorage.description,
            'submenus_count': 0,
            'dishes_count': 0,
        }

    @pytest.mark.asyncio
    async def test_delete_menu(self, client: AsyncClient):
        response = await client.delete(f'/api/v1/menus/{MenuValueStorage.id}')
        assert response.status_code == 200, response.text

    @pytest.mark.asyncio
    async def test_read_menus_after_delete(self, client: AsyncClient):
        response = await client.get('/api/v1/menus')
        assert response.status_code == 200, response.text
        assert response.json() == []
