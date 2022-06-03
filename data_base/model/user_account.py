from dataclasses import dataclass
from decimal import Decimal


@dataclass
class UserAccount:
    id: int = None
    id_user_data: int = None
    account_number: str = None
    currency: str = None
    amount: Decimal = None
