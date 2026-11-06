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

def test_create_transaction_missing_amount():
    """POST /transactions без amount → 422 Unprocessable Entity"""
    payload = {
        "payer_id": 1,
        "type": "expense",
        "split_mode": "half",
        "date": "2026-11-05"
    }
    response = client.post("/transactions", json=payload)
    assert response.status_code == 422

def test_get_budget_with_limit_and_expense():
    """GET /budget/{month} с заданным лимитом и расходами"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO budgets (user_id, category_id, month, limit_amount) VALUES (NULL, NULL, '2026-11', 5000)"
    )
    cursor.execute(
        "INSERT INTO transactions (payer_id, amount, type, split_mode, date) VALUES (1, 2000, 'expense', 'pool', '2026-11-01')"
    )
    conn.commit()
    conn.close()

    response = client.get("/budget/2026-11")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5000
    assert data["expenses"] == 2000
    assert data["remainder"] == 3000

def test_balance_after_two_half_transactions():
    """Два half-платежа от разных пользователей → баланс сходится"""
    client.post("/transactions", json={
        "payer_id": 1, "amount": 1000, "type": "expense", "split_mode": "half", "date": "2026-11-01"
    })
    client.post("/transactions", json={
        "payer_id": 2, "amount": 2000, "type": "expense", "split_mode": "half", "date": "2026-11-02"
    })

    response = client.get("/balance")
    assert response.status_code == 200
    balance = response.json()["balance"]
    # user1 заплатил 1000 (half=500 должен получить от user2)
    # user2 заплатил 2000 (half=1000 должен получить от user1)
    # Итого: user1 должен получить 1000-500=500? Нет: user1 должен получить 1000 (от платежа user2), отдать 500 (от своего)
    # Чистый баланс: user1 = +1000 - 500 = +500; user2 = -1000 + 500 = -500
    # Стоп: пересчитаем.
    # Платёж 1: payer=1, 1000, half → debt=500. balance[1]+=500, balance[2]-=500.
    # Платёж 2: payer=2, 2000, half → debt=1000. balance[2]+=1000, balance[1]-=1000.
    # Итог: balance[1] = 500-1000 = -500; balance[2] = -500+1000 = +500.
    assert balance["1"] == -500.0
    assert balance["2"] == 500.0