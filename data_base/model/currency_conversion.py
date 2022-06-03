from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class CurrencyConversion:
    id: int = None
    id_user_account_out: int = None
    id_user_account_in: int = None
    transfer_amount: Decimal = None
    exchange_rate: Decimal = None
    transaction_time: datetime = None
    balance_out: Decimal = None
    balance_in: Decimal = None
