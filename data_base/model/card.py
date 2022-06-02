from dataclasses import dataclass


@dataclass
class Card:
    id: int = None
    id_user_data: int = None
    card_number: str = None
    valid_thru: str = None
    cvv: str = None
    blocked: bool = None
    daily_limit: int = None
    internet_limit: int = None
    contactless_limit: int = None
    card_pin: str = None
    sec_online_transactions: bool = None
    sec_location: bool = None
    sec_magnetic_strip: bool = None
    sec_withdrawals_atm: bool = None
    sec_contactless: bool = None
