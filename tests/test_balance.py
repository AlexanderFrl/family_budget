
from models import Transaction, calculator_balance

def test_half_split():
    """50 на 50"""
    transactions = [Transaction(payer_id = 1,amount = 1000,split_mod="half")]
    result = calculator_balance(transactions)
    assert result == {1: 500.0, 2: -500.0}

def test_custom_split():
    """70 на 30"""
    transactions = [Transaction(payer_id = 1, amount = 1000, split_mod = "custom", split_percent = 70)]
    result = calculator_balance(transactions)   
    assert result == {1: 300.0, 2: -300.0}

def test_solo_and_pool_no_debt():
    """0"""
    transactions = [
    Transaction(payer_id = 1, amount = 500, split_mod = "solo"),
    Transaction(payer_id = 2, amount = 300, split_mod = "pool"),
    ]
    result = calculator_balance(transactions)
    assert result == {}