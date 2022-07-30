from management.conversions import dates_named_tuple
from management.validation import *
from collections import namedtuple
from random import randint


def choose_payment_type() -> str:
    """Select the type of card you want to get"""
    print("""
        Choose the type of payment: 
        1. Contactless payment
        2. Magnetic stripe payment
        3. Internet payment
        """)
    chosen_operation = get_answer(
        validation_chosen_operation,
        'Enter the selected type of payment: ',
        'Entered data contains illegal characters. Try again: ',
        (1, 3))
    match chosen_operation:
        case '1':
            return 'Contactless payment'
        case '2':
            return 'Magnetic stripe payment'
        case '3':
            return 'Internet payment'


def choose_card_type() -> str:
    """Select the type of card you want to get"""
    print("""
        Select the type of card you want to create: 
        1. STANDARD
        2. SINGLE-USE VIRTUAL
        3. MULTI-USE VIRTUAL
        """)
    chosen_operation = get_answer(
        validation_chosen_operation,
        'Enter chosen card type: ',
        'Entered data contains illegal characters. Try again: ',
        (1, 3))
    match chosen_operation:
        case '1':
            return 'STANDARD'
        case '2':
            return 'SINGLE-USE VIRTUAL'
        case '3':
            return 'MULTI-USE VIRTUAL'


def choose_currency(text: str) -> str:
    """Select the currency for which you want to perform the operation"""
    print(f"""
        {text}: 
        1. GBP
        2. USD
        3. CHF
        4. EUR
        """)
    chosen_operation = get_answer(
        validation_chosen_operation,
        'Enter chosen currency: ',
        'Entered data contains illegal characters. Try again: ',
        (1, 4))
    match chosen_operation:
        case '1':
            return 'GBP'
        case '2':
            return 'USD'
        case '3':
            return 'CHF'
        case '4':
            return 'EUR'


def choose_limit_card(used_card: namedtuple, last_letter: int, operation_range: int) -> str:
    """Select the type of transaction you want to perform"""
    text = """
            Select the type of card limit you want to change: 
            1. Daily limit
            2. Internet limit
            3. Contactless limit
            """
    print(text[:last_letter]) if used_card.card_type == "SINGLE-USE VIRTUAL" else print(text)
    chosen_operation = get_answer(
        validation_chosen_operation,
        'Enter chosen limit type: ',
        'Entered data contains illegal characters. Try again: ',
        (1, operation_range))
    match chosen_operation:
        case '1':
            return 'Daily limit'
        case '2':
            return 'Internet limit'
        case '3':
            return 'Contactless limit'


def get_dates() -> namedtuple:
    """Enter and validate dates for which you want to find transactions"""
    start_date = datetime.fromisoformat(get_answer(
        validation_datetime,
        'Enter the start date: ',
        'Entered date doesn"t exist. Enter the date in this format -  2000-12-31'))
    end_date = datetime.fromisoformat(get_answer(
        validation_datetime,
        'Enter the end date: ',
        'Entered date doesn"t exist. Enter the date in this format -  2000-12-31'))
    return dates_named_tuple((start_date, end_date))


def generate_random_number(range_min: int, range_max: int) -> str:
    """Generate a random number that can be used to simulate some number"""
    return ''.join([str(randint(0, 9)) for _ in range(range_min, range_max)])
