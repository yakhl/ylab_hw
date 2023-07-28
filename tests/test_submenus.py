from fastapi.testclient import TestClient

from main import app
from conftest import MenuValueStorage, SubmenuValueStorage


client = TestClient(app)


def test_create_menu():
    MenuValueStorage.title = "Menu title 1"
    MenuValueStorage.description = "Menu description 1"
    response = client.post(
        "/api/v1/menus",
        json={
            "title": MenuValueStorage.title,
            "description": MenuValueStorage.description,
        },
    )
    assert response.status_code == 201, response.text
    data_out = response.json()
    MenuValueStorage.id = data_out["id"]


def test_read_submenus_in_empty_menu():
    response = client.get(f"/api/v1/menus/{MenuValueStorage.id}/submenus")
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_create_submenu():
    SubmenuValueStorage.title = "Submenu title 1"
    SubmenuValueStorage.description = "Submenu description 1"
    response = client.post(
        f"/api/v1/menus/{MenuValueStorage.id}/submenus",
        json={
            "title": SubmenuValueStorage.title,
            "description": SubmenuValueStorage.description,
        },
    )
    assert response.status_code == 201, response.text
    data_out = response.json()
    SubmenuValueStorage.id = data_out["id"]
    assert data_out == {
        "id": SubmenuValueStorage.id,
        "title": SubmenuValueStorage.title,
        "description": SubmenuValueStorage.description,
        "menu_id": MenuValueStorage.id,
        "dishes_count": 0,
    }


def test_read_submenus_after_create():
    response = client.get(f"/api/v1/menus/{MenuValueStorage.id}/submenus")
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert isinstance(data_out, list) and len(data_out) == 1
    submenu = data_out[0]
    assert submenu == {
        "id": SubmenuValueStorage.id,
        "title": SubmenuValueStorage.title,
        "description": SubmenuValueStorage.description,
        "menu_id": MenuValueStorage.id,
        "dishes_count": 0,
    }


def test_read_submenu_after_create():
    response = client.get(
        f"/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}"
    )
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert data_out == {
        "id": SubmenuValueStorage.id,
        "title": SubmenuValueStorage.title,
        "description": SubmenuValueStorage.description,
        "menu_id": MenuValueStorage.id,
        "dishes_count": 0,
    }


def test_update_submenu():
    SubmenuValueStorage.title = "Updated submenu title 1"
    SubmenuValueStorage.description = "Updated submenu description 1"
    response = client.patch(
        f"/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}",
        json={
            "title": SubmenuValueStorage.title,
            "description": SubmenuValueStorage.description,
        },
    )
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert data_out == {
        "id": SubmenuValueStorage.id,
        "title": SubmenuValueStorage.title,
        "description": SubmenuValueStorage.description,
        "menu_id": MenuValueStorage.id,
        "dishes_count": 0,
    }


def test_read_submenu_after_update():
    response = client.get(
        f"/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}"
    )
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert data_out == {
        "id": SubmenuValueStorage.id,
        "title": SubmenuValueStorage.title,
        "description": SubmenuValueStorage.description,
        "menu_id": MenuValueStorage.id,
        "dishes_count": 0,
    }


def test_delete_submenu():
    response = client.delete(
        f"/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}"
    )
    assert response.status_code == 200, response.text


def test_read_submenus_after_delete():
    response = client.get(f"/api/v1/menus/{MenuValueStorage.id}/submenus")
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_read_submenu_after_delete():
    response = client.get(
        f"/api/v1/menus/{MenuValueStorage.id}/submenus/{SubmenuValueStorage.id}"
    )
    assert response.status_code == 404, response.text
    data_out = response.json()
    assert data_out["detail"] == "submenu not found"


def test_delete_menu():
    response = client.delete(f"/api/v1/menus/{MenuValueStorage.id}")
    assert response.status_code == 200, response.text


def test_read_menus_after_delete():
    response = client.get("/api/v1/menus")
    assert response.status_code == 200, response.text
    assert response.json() == []
