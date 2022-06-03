from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class CardTransaction:
    id: int = None
    id_user_account: int = None
    transaction_time: datetime = None
    amount: Decimal = None
    commission: Decimal = None
    balance: Decimal = None
    payer_name: str = None
