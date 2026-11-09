import pytest
import database

@pytest.fixture(autouse=True, scope="session")
def init_database():
    """Создает таблицы один раз на сессию тестов (локально и в CI)"""
    database.init_db()

