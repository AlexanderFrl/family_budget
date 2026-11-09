from fastapi.testclient import TestClient
import database
from server import app

client = TestClient(app)

def setup_function():
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM categories")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (1, 'user1', 'hash1')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (2, 'user2', 'hash2')")
    conn.commit()
    conn.close()

def seed_report_data():
    """Данные отчёта: 2 категории, траты 100+200 (еда), 50 (транспорт), 25 без категории, income 999"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES ('еда')")
    food_id = cursor.lastrowid
    cursor.execute("INSERT INTO categories (name) VALUES ('транспорт')")
    transport_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO transactions (payer_id, category_id, amount, type, split_mode, date) "
        "VALUES (1, ?, 100, 'expense', 'solo', '2026-11-01')", (food_id,))
    cursor.execute(
        "INSERT INTO transactions (payer_id, category_id, amount, type, split_mode, date) "
        "VALUES (1, ?, 200, 'expense', 'solo', '2026-11-02')", (food_id,))
    cursor.execute(
        "INSERT INTO transactions (payer_id, category_id, amount, type, split_mode, date) "
        "VALUES (1, ?, 50, 'expense', 'solo', '2026-11-03')", (transport_id,))
    cursor.execute(
        "INSERT INTO transactions (payer_id, category_id, amount, type, split_mode, date) "
        "VALUES (1, NULL, 25, 'expense', 'solo', '2026-11-04')")
    cursor.execute(
        "INSERT INTO transactions (payer_id, amount, type, split_mode, date) "
        "VALUES (1, 999, 'income', 'solo', '2026-11-05')")
    conn.commit()
    conn.close()


def test_report_totals_by_category():
    """GET /report/{month}: сумма по категориям, income не попадает"""
    seed_report_data()
    response = client.get("/report/2026-11")
    assert response.status_code == 200
    data = response.json()

    totals = {x["category"]: x["total"] for x in data["by_category"]}
    assert totals["еда"] == 300
    assert totals["транспорт"] == 50
    assert totals["без категории"] == 25
    assert data["total"] == 375

def test_report_empty_month():
    response = client.get("/report/2025-11")
    assert response.status_code == 200
    data = response.json()
    assert data["by_category"] == []
    assert data["total"] == 0