def test_get_empty_todos_list(client):
    response = client.get("/todos/")

    assert response.status_code == 200
    assert response.json() == []
