users (id, username, password_hash, created_at)
-- 2 записи: ты и партнёр, без регистрации

categories (id, user_id, name, monthly_limit)
-- лимиты по категориям для каждого

transactions (id, user_id, category_id, amount, type, paid_by, note, date)
-- type: income/expense; paid_by: кто заплатил (для совместных трат)

budgets (id, user_id, month, category_id, limit_amount)
-- месячные лимиты (можно вынести из categories)


CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);
CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  is_shared INTEGER DEFAULT 0
);
CREATE TABLE budgets (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),          -- NULL = общий бюджет пары
  category_id INTEGER REFERENCES categories(id), -- NULL = общий лимит месяца
  month TEXT NOT NULL,                            -- формат '2026-11'
  limit_amount REAL NOT NULL
);
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY,
  payer_id INTEGER NOT NULL REFERENCES users(id),
  category_id INTEGER REFERENCES categories(id),
  amount REAL NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('income','expense')),
  split_mode TEXT NOT NULL DEFAULT 'solo'
    CHECK (split_mode IN ('solo','half','custom','pool')),
  split_percent REAL,   -- доля плательщика в custom, 0–100
  date TEXT NOT NULL,
  note TEXT
);