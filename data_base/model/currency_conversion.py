from dataclasses import dataclass


@dataclass
class CurrencyConversion:
    id: int = None
    id_user_account_out: int = None
    id_user_account_in: int = None
    transfer_amount: str = None
    exchange_rate: str = None
    transaction_time: str = None
    balance_out: str = None
    balance_in: str = None
