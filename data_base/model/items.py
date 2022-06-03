from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal


@dataclass
class User:
    id: int = None
    login: str = None
    password: str = None
    creation_date: datetime = None


@dataclass
class UserData:
    id: int = None
    id_user: int = None
    name: str = None
    surname: str = None
    country: str = None
    address: str = None
    email: str = None
    phone: str = None


@dataclass
class Service:
    id: int = None
    id_user_data: int = None
    user_account_id: int = None


@dataclass
class Card:
    id: int = None
    id_user_data: int = None
    card_number: str = None
    valid_thru: date = None
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


@dataclass
class UserAccount:
    id: int = None
    id_user_data: int = None
    account_number: str = None
    currency: str = None
    amount: Decimal = None


@dataclass
class CardTransaction:
    id: int = None
    id_user_account: int = None
    transaction_time: datetime = None
    amount: Decimal = None
    commission: Decimal = None
    balance: Decimal = None
    payer_name: str = None


@dataclass
class CurrencyExpense:
    id: int = None
    id_user_account: int = None
    transfer_amount: Decimal = None
    exchange_rate: Decimal = None
    transaction_time: datetime = None
    balance: Decimal = None


@dataclass
class CurrencyIncome:
    id: int = None
    id_user_account: int = None
    transfer_amount: Decimal = None
    exchange_rate: Decimal = None
    transaction_time: datetime = None
    balance: Decimal = None


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
