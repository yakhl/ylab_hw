import pytest
from httpx import AsyncClient

from tests.conftest import DishValueStorage, MenuValueStorage, SubmenuValueStorage


class TestDish:
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
    async def test_read_dishes_in_empty_submenu(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes')
        assert response.status_code == 200, response.text
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_dish(self, client: AsyncClient):
        DishValueStorage.title = 'Dish title 1'
        DishValueStorage.description = 'Dish description 1'
        DishValueStorage.price = 12.5345
        response = await client.post(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes',
            json={
                'title': DishValueStorage.title,
                'description': DishValueStorage.description,
                'price': DishValueStorage.price,
            },
        )
        assert response.status_code == 201, response.text
        data_out = response.json()
        DishValueStorage.id = data_out['id']
        assert data_out == {
            'id': DishValueStorage.id,
            'title': DishValueStorage.title,
            'description': DishValueStorage.description,
            'submenu_id': SubmenuValueStorage.id,
            'price': str(round(DishValueStorage.price, 2)),
        }

    @pytest.mark.asyncio
    async def test_read_dishes_after_create(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes')
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert isinstance(data_out, list) and len(data_out) == 1
        assert [
            {
                'id': DishValueStorage.id,
                'title': DishValueStorage.title,
                'description': DishValueStorage.description,
                'submenu_id': SubmenuValueStorage.id,
                'price': str(round(DishValueStorage.price, 2)),
            }
        ]

    @pytest.mark.asyncio
    async def test_read_dish_after_create(self, client: AsyncClient):
        response = await client.get(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes/{DishValueStorage.id}'
        )
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert data_out == {
            'id': DishValueStorage.id,
            'title': DishValueStorage.title,
            'description': DishValueStorage.description,
            'submenu_id': SubmenuValueStorage.id,
            'price': str(round(DishValueStorage.price, 2)),
        }

    @pytest.mark.asyncio
    async def test_update_dish(self, client: AsyncClient):
        DishValueStorage.title = 'Updated dish title 1'
        DishValueStorage.description = 'Updated dish description 1'
        DishValueStorage.price = 11.452
        response = await client.patch(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes/{DishValueStorage.id}',
            json={
                'title': DishValueStorage.title,
                'description': DishValueStorage.description,
                'price': DishValueStorage.price,
            },
        )
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert data_out == {
            'id': DishValueStorage.id,
            'title': DishValueStorage.title,
            'description': DishValueStorage.description,
            'submenu_id': SubmenuValueStorage.id,
            'price': str(round(DishValueStorage.price, 2)),
        }

    @pytest.mark.asyncio
    async def test_read_dishes_after_update(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes')
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert isinstance(data_out, list) and len(data_out) == 1
        assert [
            {
                'id': DishValueStorage.id,
                'title': DishValueStorage.title,
                'description': DishValueStorage.description,
                'submenu_id': SubmenuValueStorage.id,
                'price': str(round(DishValueStorage.price, 2)),
            }
        ]

    @pytest.mark.asyncio
    async def test_read_dish_after_update(self, client: AsyncClient):
        response = await client.get(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes/{DishValueStorage.id}'
        )
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert data_out == {
            'id': DishValueStorage.id,
            'title': DishValueStorage.title,
            'description': DishValueStorage.description,
            'submenu_id': SubmenuValueStorage.id,
            'price': str(round(DishValueStorage.price, 2)),
        }

    @pytest.mark.asyncio
    async def test_delete_dish(self, client: AsyncClient):
        response = await client.delete(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes/{DishValueStorage.id}'
        )
        assert response.status_code == 200, response.text

    @pytest.mark.asyncio
    async def test_read_dishes_after_delete(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes')
        assert response.status_code == 200, response.text
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_read_dish_after_delete(self, client: AsyncClient):
        response = await client.get(
            f'/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}/dishes/{DishValueStorage.id}'
        )
        assert response.status_code == 404, response.text
        data_out = response.json()
        assert data_out['detail'] == 'dish not found'

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
    async def test_delete_menu(self, client: AsyncClient):
        response = await client.delete(f'/api/v1/menus/{MenuValueStorage.id}')
        assert response.status_code == 200, response.text

    @pytest.mark.asyncio
    async def test_read_menus_after_delete(self, client: AsyncClient):
        response = await client.get('/api/v1/menus')
        assert response.status_code == 200, response.text
        assert response.json() == []
