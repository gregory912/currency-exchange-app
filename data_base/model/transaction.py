from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Transaction:
    id: int = None
    id_user_account: int = None
    payment: str = None
    payout: str = None
    transfer_title: str = None
    transaction_time: datetime = None
    amount: Decimal = None
    balance: Decimal = None
    payer_name: str = None
    payer_account_number: str = None
