from fastapi.testclient import TestClient

import database
from server import app

client = TestClient(app)

def setup_function():
    """Перед каждым тестом: очистка таблиц и сид пользователей"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM categories")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (1, 'user1', 'hash1')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (2, 'user2', 'hash2')")
    conn.commit()
    conn.close()

def test_create_category_visible_in_list():
    """POST /categories -> 201, категория видна в GET"""
    response = client.post("/categories", json={"name":"food"})
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "food"
    assert "id" in created

    response = client.get("/categories")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "food" in names

def test_delete_category_removes_it():
    """DELETE /categories/{id} -> 204, категория исчезла из GET"""
    created = client.post("/categories", json = {"name":"transport"}).json()
    category_id = created["id"]

    response = client.delete(f"/categories/{category_id}")
    assert response.status_code==204

    response = client.get("/categories")
    names = [c["name"] for c in response.json()]
    assert "transport" not in names

def test_delete_missing_category_404():
    """DELETE несуществующего id -> 404"""
    response = client.delete("/categories/999")
    assert response.status_code == 404