from dataclasses import dataclass


@dataclass
class CardTransaction:
    id: int = None
    id_user_account: int = None
    payment: str = None
    payout: str = None
    transfer_title: str = None
    transaction_time: str = None
    amount: str = None
    balance: str = None
    payer_name: str = None
    payer_account_number: str = None
