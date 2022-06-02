from dataclasses import dataclass


@dataclass
class UserAccount:
    id: int = None
    id_user_data: int = None
    account_number: str = None
    currency: str = None
    amount: str = None
