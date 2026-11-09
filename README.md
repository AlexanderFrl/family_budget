# Family Budget API 🍏

![CI Status](https://github.com/AlexanderFrl/family_budget/actions/workflows/ci.yaml/badge.svg)

REST API для учёта семейного бюджета с поддержкой разделения трат, категорий и отчётов.

## 🚀 Стек

- **Backend**: Python 3.13, FastAPI, SQLite, Pydantic v2
- **Testing**: Pytest, TestClient, Allure
- **CI/CD**: GitHub Actions (pytest на push/PR)

## 🏗 Архитектура

Проект построен по принципу разделения ответственности:

- `database.py` — слой работы с БД: схема 4 таблиц, подключения с `PRAGMA foreign_keys = ON`, индексы.
- `models.py` — бизнес-логика: `dataclass Transaction` и функция `calculate_balance()`.
- `server.py` — HTTP-слой: роуты FastAPI, Pydantic-модели валидации.
- `tests/` — пирамида тестов: unit (balance), integration (API), db-level (FK/CHECK/CASCADE).

### Схема БД

| Таблица | Назначение | Ключевые ограничения |
|---------|-----------|---------------------|
| `users` | Пользователи | `username` UNIQUE NOT NULL |
| `categories` | Справочник трат | `name` NOT NULL |
| `transactions` | Операции | `CHECK (amount > 0)`, FK → users (CASCADE), FK → categories (SET NULL) |
| `budgets` | Месячные лимиты | FK → users, FK → categories |

## 🛠 API Endpoints

| Метод | Путь | Описание | Статус |
|-------|------|----------|--------|
| POST | `/transactions` | Добавить трату | 200 |
| GET | `/balance` | Баланс между пользователями | 200 |
| GET | `/budget/{month}` | Остаток по лимиту за месяц | 200 |
| GET | `/report/{month}` | Отчёт по категориям (JOIN + GROUP BY) | 200 |
| POST | `/categories` | Создать категорию | 201 |
| GET | `/categories` | Список всех категорий | 200 |
| DELETE | `/categories/{id}` | Удалить категорию | 204 / 404 |

Swagger UI: http://localhost:8000/docs

## 🏃‍♂️ Как запустить

```bash
git clone https://github.com/AlexanderFrl/family_budget.git
cd family_budget
python3 -m venv family && source family/bin/activate
pip install -r requirements.txt
python server.py