from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager
import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    print("✅ БД инициализирована")
    yield


app = FastAPI(title="Family Budget API", lifespan=lifespan)


class TransactionCreate(BaseModel):
    payer_id: int
    category_id: Optional[int] = None
    amount: float
    type: str
    split_mode: str
    split_percent: Optional[float] = None
    date: Optional[str] = None
    note: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    payer_id: int
    amount: float
    type: str
    split_mode: str
    date: str
class CategoryCreate(BaseModel):
    name:str
    is_shared: int = 0

class CategoryResponse(BaseModel):
    id: int
    name: str
    is_shared: int

@app.post("/categories", status_code=201, response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    """Создать категорию"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categories (name, is_shared) VALUES (?, ?)",
        (category.name, category.is_shared)
    )
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return CategoryResponse(id=category_id, name=category.name, is_shared=category.is_shared)

@app.get("/categories", response_model=list[CategoryResponse])
async def list_category():
    """Список всех категорий"""
    conn = database.get_connection()
    rows = conn.execute("SELECT id, name, is_shared FROM categories").fetchall()
    conn.close()
    return [CategoryResponse(id=r["id"], name=r["name"], is_shared=r["is_shared"]) for r in rows]

@app.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int):
    """Удалить категорию; если нет 404"""
    conn = database.get_connection()
    row = conn.execute("SELECT id FROM categories WHERE id = ?", (category_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail= "Category not found")
    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    return Response(status_code=204)

@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate):
    conn = database.get_connection()
    cursor = conn.cursor()
    date = transaction.date or datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO transactions (payer_id, category_id, amount, type, split_mode, split_percent, date, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction.payer_id,
        transaction.category_id,
        transaction.amount,
        transaction.type,
        transaction.split_mode,
        transaction.split_percent,
        date,
        transaction.note
    ))
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()

    return TransactionResponse(
        id=transaction_id,
        payer_id=transaction.payer_id,
        amount=transaction.amount,
        type=transaction.type,
        split_mode=transaction.split_mode,
        date=date
    )


@app.get("/balance")
async def get_balance():
    from models import calculate_balance, Transaction
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT payer_id, amount, split_mode, split_percent FROM transactions WHERE split_mode IN ('half', 'custom')")
    rows = cursor.fetchall()
    conn.close()

    transactions = [
        Transaction(
            payer_id=row["payer_id"],
            amount=row["amount"],
            split_mode=row["split_mode"],
            split_percent=row["split_percent"]
        )
        for row in rows
    ]
    balance = calculate_balance(transactions)
    return {"balance": balance}


@app.get("/budget/{month}")
async def get_budget(month: str):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT limit_amount FROM budgets WHERE month = ? AND user_id IS NULL AND category_id IS NULL",
                   (month,))
    row = cursor.fetchone()
    total_limit = row["limit_amount"] if row else 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND strftime('%Y-%m', date) = ?",
                   (month,))
    row = cursor.fetchone()
    total_expenses = row[0] or 0
    conn.close()

    remainder = total_limit - total_expenses
    return {"month": month, "limit": total_limit, "expenses": total_expenses, "remainder": remainder}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)