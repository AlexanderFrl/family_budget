from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

import database


def seed_users():
    """Создаем двух тестовых пользователей, если их нет"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (1, 'user1', 'hash1')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (2, 'user2', 'hash2')")
    conn.commit()
    conn.close()



def test_create_transaction():
    """POST/transaction создает запись и возвращает 200"""
    payload = {
        "payer_id" : 1,
        "amount" : 1500.0,
        "type" : "expense",
        "split_mode" : "half",
        "date" : "05_11_2026"
    }
    response = client.post("/transactions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 1500.0
    assert data["split_mode"] == "half"
    assert "id" in data

def test_get_balance_empty():
    """GET /balance возвращает пустой баланс при отсутствии транзакций"""
    response = client.get("/balance")
    assert response.status_code == 200
    assert response.json()["balance"] == {}

def test_get_budget_no_limit():
    """GET /budget/{month} возвращает 0 лимит, если не задан"""
    response = client.get("/budget/2026-11")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 0
    assert data["expenses"] == 0
    assert data["remainder"] == 0

def setup_function():
    """Выполнять перед каждым тестом. Создает пользователей и очищает транзакции"""
    seed_users()
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")
    conn.commit()
    conn.close()