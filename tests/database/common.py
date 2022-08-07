import random
from datetime import datetime, date
from decimal import Decimal


def dict_to_tuple(dict_: dict) -> tuple:
    """Convert dict to tuple"""
    return tuple([x for x in dict_.values()])


def draw_numbers(elements: int) -> str:
    """The method randomizes the numbers and returns a string"""
    return ''.join([str(random.randint(1, 9)) for _ in range(elements)])


def draw_letters(elements: int) -> str:
    """The method randomizes the numbers and returns a string"""
    return ''.join([chr(random.randint(97, 122)) for _ in range(elements)])


def get_current_time() -> datetime:
    """Get today's date without milliseconds"""
    current_time = datetime.now().strftime("%Y %m %d %H %M %S")
    return datetime.strptime(current_time, "%Y %m %d %H %M %S")


def get_user_account(id_user_data: int, acc_number: str, amount: float) -> dict:
    """Return properly prepared data in the form of dict for the user_account table"""
    return {
        "id_user_data": id_user_data, "account_number": acc_number,
        "currency": "USD", "balance": Decimal(amount)}


def get_user_data(email: str, digits_for_phone: int, digits_to_log_in: int) -> dict:
    """Return properly prepared data in the form of dict for the user_data table"""
    return {
        "name": "name", "surname": "surname", "country": "country", "address": "address",
        "email": email, "phone": draw_numbers(digits_for_phone),
        "login": draw_letters(digits_to_log_in), "password": draw_letters(digits_to_log_in),
        "creation_date": get_current_time(), "main_currency": "GBP"}


def get_cards(card_number: str) -> dict:
    """Return properly prepared data in the form of dict for the cards table"""
    return {
        "card_number": card_number, "valid_thru": date.today(), "cvv": "123",
        "blocked": False, "daily_limit": 2000, "internet_limit": 1000,
        "contactless_limit": 100, "card_pin": "1234", "sec_online_transactions": True,
        "sec_location": False, "sec_magnetic_strip": False, "sec_withdrawals_atm": True,
        "sec_contactless": True, "card_name": "card name", "card_type": "STANDARD",
        "main_currency": "GBP"}


def get_card_transaction(balance: int) -> dict:
    """Return properly prepared data in the form of dict for the card_transactions table"""
    return {
        "transaction_time": get_current_time(),
        "amount": Decimal(1000.00),
        "commission_in_main_user_currency": Decimal(2.0),
        "balance": Decimal(balance),
        "payer_name": "payer_name",
        "payout": "YES",
        "payment": "NO",
        "rate_to_main_card_currency": Decimal(1.0),
        "transaction_type": "Internet payment",
        "rate_tu_used_account": Decimal(1.0),
        "payer_account_number": "payer_account_number",
        "amount_in_main_user_currency": Decimal(800)
    }


def get_currency_exchange(id_user_account_out: int, id_user_account_in: int, transaction_time: datetime) -> dict:
    """Return properly prepared data in the form of dict for the card_transactions table"""
    return {
        "id_user_account_out": id_user_account_out,
        "transfer_amount_out": Decimal(1000),
        "exchange_rate_out": Decimal(1.0),
        "balance_out": Decimal(1500),
        "id_user_account_in": id_user_account_in,
        "transfer_amount_in": Decimal(800),
        "exchange_rate_in": Decimal(0.8),
        "balance_in": Decimal(1800),
        "transaction_time": transaction_time,
        "amount_in_main_user_currency": Decimal(700),
        "commission_in_main_user_currency": Decimal(50)
    }

