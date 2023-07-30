from .conftest import MenuValueStorage, client


def test_read_menus_in_empty_db():
    response = client.get("/api/v1/menus")
    assert response.status_code == 200, response.text
    assert response.json() == []


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
    assert data_out == {
        "id": MenuValueStorage.id,
        "title": MenuValueStorage.title,
        "description": MenuValueStorage.description,
        "submenus_count": 0,
        "dishes_count": 0,
    }


def test_read_menus_after_create():
    response = client.get("/api/v1/menus")
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert isinstance(data_out, list) and len(data_out) == 1
    menu = data_out[0]
    assert menu == {
        "id": MenuValueStorage.id,
        "title": MenuValueStorage.title,
        "description": MenuValueStorage.description,
        "submenus_count": 0,
        "dishes_count": 0,
    }


def test_read_menu_after_create():
    response = client.get(f"/api/v1/menus/{MenuValueStorage.id}")
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert data_out == {
        "id": MenuValueStorage.id,
        "title": MenuValueStorage.title,
        "description": MenuValueStorage.description,
        "submenus_count": 0,
        "dishes_count": 0,
    }


def test_update_menu():
    MenuValueStorage.title = "Updated menu title 1"
    MenuValueStorage.description = "Updated menu description 1"
    response = client.patch(
        f"/api/v1/menus/{MenuValueStorage.id}",
        json={
            "title": MenuValueStorage.title,
            "description": MenuValueStorage.description,
        },
    )
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert data_out == {
        "id": MenuValueStorage.id,
        "title": MenuValueStorage.title,
        "description": MenuValueStorage.description,
        "submenus_count": 0,
        "dishes_count": 0,
    }


def test_read_menu_after_update():
    response = client.get(f"/api/v1/menus/{MenuValueStorage.id}")
    assert response.status_code == 200, response.text
    data_out = response.json()
    assert data_out == {
        "id": MenuValueStorage.id,
        "title": MenuValueStorage.title,
        "description": MenuValueStorage.description,
        "submenus_count": 0,
        "dishes_count": 0,
    }


def test_delete_menu():
    response = client.delete(f"/api/v1/menus/{MenuValueStorage.id}")
    assert response.status_code == 200, response.text


def test_read_menus_after_delete():
    response = client.get("/api/v1/menus")
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_read_menu_after_delete():
    response = client.get(f"/api/v1/menus/{MenuValueStorage.id}")
    assert response.status_code == 404, response.text
    data_out = response.json()
    assert data_out["detail"] == "menu not found"
