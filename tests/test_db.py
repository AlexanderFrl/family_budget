import sqlite3
import pytest
import database

def setup_function():
    """Перед каждым тестом очистка таблицы и сид пользователя"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM categories")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (1, 'user1', 'hash1')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (2, 'user2', 'hash2')")
    conn.commit()
    conn.close()

def test_fk_violation_payer_not_exists():
    """INSERT траты с несуществующим payer_id → IntegrityError"""
    conn = database.get_connection()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO transactions (payer_id, amount, type, split_mode, date)"
            "VALUES (999, 100, 'expense', 'solo', '2026-11-09')"
        )
    conn.close()

def test_check_amount_positive():
    """Отрицательная сумма отклоняется CHECK (amount > 0)"""
    conn = database.get_connection()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO transactions (payer_id, amount, type, split_mode, date)"
            "VALUES (1, -100, 'expense', 'solo', '2026-11-09')"
        )
    conn.close()

def test_unique_username():
    """Второй пользователь с тем же username → IntegrityError (UNIQUE)"""
    conn = database.get_connection()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES ('user1', 'hashX')"
        )
    conn.close()


def test_not_null_date():
    """INSERT траты без date → IntegrityError (NOT NULL)"""
    conn = database.get_connection()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO transactions (payer_id, amount, type, split_mode) "
            "VALUES (1, 100, 'expense', 'solo')"
        )
    conn.close()


def test_on_delete_set_null():
    """Удаление категории обнуляет category_id трат (ON DELETE SET NULL)"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES ('food')")
    category_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO transactions (payer_id, category_id, amount, type, split_mode, date) "
        "VALUES (1, ?, 300, 'expense', 'solo', '2026-11-09')",
        (category_id,),
    )
    conn.commit()

    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()

    row = conn.execute("SELECT category_id FROM transactions").fetchone()
    conn.close()
    assert row[0] is None


def test_on_delete_cascade():
    """Удаление пользователя удаляет его траты (ON DELETE CASCADE)"""
    conn = database.get_connection()
    conn.execute(
        "INSERT INTO transactions (payer_id, amount, type, split_mode, date) "
        "VALUES (1, 500, 'expense', 'solo', '2026-11-09')"
    )
    conn.commit()

    conn.execute("DELETE FROM users WHERE id = 1")
    conn.commit()

    row = conn.execute("SELECT COUNT(*) FROM transactions WHERE payer_id = 1").fetchone()
    conn.close()
    assert row[0] == 0