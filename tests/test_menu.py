import pytest
from httpx import AsyncClient

from tests.conftest import MenuValueStorage


class TestMenu:
    @pytest.mark.asyncio
    async def test_read_menus_in_empty_db(self, client: AsyncClient):
        response = await client.get('/api/v1/menus')
        assert response.status_code == 200, response.text
        assert response.json() == []

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
        assert data_out == {
            'id': MenuValueStorage.id,
            'title': MenuValueStorage.title,
            'description': MenuValueStorage.description,
            'submenus_count': 0,
            'dishes_count': 0,
        }

    @pytest.mark.asyncio
    async def test_read_menus_after_create(self, client: AsyncClient):
        response = await client.get('/api/v1/menus')
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert isinstance(data_out, list) and len(data_out) == 1
        assert [
            {
                'id': MenuValueStorage.id,
                'title': MenuValueStorage.title,
                'description': MenuValueStorage.description,
                'submenus_count': 0,
                'dishes_count': 0,
            }
        ]

    @pytest.mark.asyncio
    async def test_read_menu_after_create(self, client: AsyncClient):
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
    async def test_update_menu(self, client: AsyncClient):
        MenuValueStorage.title = 'Updated menu title 1'
        MenuValueStorage.description = 'Updated menu description 1'
        response = await client.patch(
            f'/api/v1/menus/{MenuValueStorage.id}',
            json={
                'title': MenuValueStorage.title,
                'description': MenuValueStorage.description,
            },
        )
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
    async def test_read_menus_after_update(self, client: AsyncClient):
        response = await client.get('/api/v1/menus')
        assert response.status_code == 200, response.text
        data_out = response.json()
        assert isinstance(data_out, list) and len(data_out) == 1
        assert [
            {
                'id': MenuValueStorage.id,
                'title': MenuValueStorage.title,
                'description': MenuValueStorage.description,
                'submenus_count': 0,
                'dishes_count': 0,
            }
        ]

    @pytest.mark.asyncio
    async def test_read_menu_after_update(self, client: AsyncClient):
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

    @pytest.mark.asyncio
    async def test_read_menu_after_delete(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus/{MenuValueStorage.id}')
        assert response.status_code == 404, response.text
        data_out = response.json()
        assert data_out['detail'] == 'menu not found'
