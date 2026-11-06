from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    payer_id:int
    amount:float
    split_mode: str #
    split_percent: Optional[float] = None #castom

def calculate_balance(transactions:list[Transaction]) -> dict[int,float]:

    balance={}
    for t in transactions:
        if t.split_mode=="solo" or t.split_mode=="pool":
            continue
        if t.split_mode=="half":
            debt = t.amount / 2
        else:
            debt = t.amount * (100 - t.split_percent) / 100

        balance[t.payer_id] = balance.get(t.payer_id, 0) + debt
        other_id = 2 if t.payer_id == 1 else 1
        balance[other_id] = balance.get(other_id,0) - debt

    return balance
