import sqlite3
import os

DB_PATH = "budget.db"

def get_connection():
    """Возвращает подключение к БД с включенным FOREIGN KEY"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row #Доступ к колоннам по имени  
    return conn

def init_db():
    """Создание таблицы если их еще нет. Вызов при старте"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_shared INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category_id INTEGER,
            month TEXT NOT NULL,
            limit_amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payer_id INTEGER NOT NULL,
            category_id INTEGER,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            split_mode TEXT NOT NULL DEFAULT 'solo' CHECK (split_mode IN ('solo', 'half', 'custom', 'pool')),
            split_percent REAL,
            date TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (payer_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"База {DB_PATH} инициализирована")