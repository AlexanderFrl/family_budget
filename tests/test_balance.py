
from models import Transaction, calculate_balance

def test_half_split():
    """50 на 50"""
    transactions = [Transaction(payer_id = 1,amount = 1000,split_mode="half")]
    result = calculate_balance(transactions)
    assert result == {1: 500.0, 2: -500.0}

def test_custom_split():
    """70 на 30"""
    transactions = [Transaction(payer_id = 1, amount = 1000, split_mode = "custom", split_percent = 70)]
    result = calculate_balance(transactions)
    assert result == {1: 300.0, 2: -300.0}

def test_solo_and_pool_no_debt():
    """0"""
    transactions = [
    Transaction(payer_id = 1, amount = 500, split_mode = "solo"),
    Transaction(payer_id = 2, amount = 300, split_mode = "pool"),
    ]
    result = calculate_balance(transactions)
    assert result == {}