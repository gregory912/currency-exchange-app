from dataclasses import dataclass


@dataclass
class CardTransaction:
    id: int = None
    id_user_account: int = None
    transaction_time: str = None
    amount: str = None
    commission: str = None
    balance: str = None
    payer_name: str = None
