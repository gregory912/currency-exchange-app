from re import match
from os import path
from typing import Callable
from datetime import datetime


def validation_of_answer(entered_value: str) -> bool:
    """Check is the answer is y or n"""
    return False if entered_value != 'Y' and entered_value != 'N' else True


def validation_alnum_and_not_digit(entered_value: str) -> bool:
    """Check if the entered value is alphanumeric and is not digits"""
    return True if entered_value.isalnum() and not entered_value.isdigit() else False


def validation_alpha(entered_item: str) -> bool:
    """Check if the entered value contains only letters"""
    return True if entered_item.isalpha() else False


def validation_digit(entered_item: str, min_length: int, max_length: int) -> bool:
    """Check if the entered value contains only digits"""
    return True if entered_item.isdigit() and min_length <= len(entered_item) <= max_length else False


def validation_space_or_alpha_not_digit(entered_item: str) -> bool:
    """Check if the entered value contains space, letters"""
    if not entered_item:
        return False
    if entered_item[:1] == ' ' or entered_item[-1:] == ' ':
        return False
    if entered_item.replace(' ', '').isdigit():
        return False
    for x in entered_item:
        if not (x == ' ' or x.isalnum()):
            return False
    return True


def validation_decimal(entered_item: str) -> bool:
    """Check if the entered number is Decimal"""
    return True if match(r'\d+\.\d+', entered_item) or entered_item.isdigit() else False


def validation_email(entered_item: str) -> bool:
    """Check if the value provided is an email address"""
    return True if match(r'^\S+@\S+\.\S+$', entered_item) else False


def validation_chosen_operation(entered_item: str, min_range: int, max_range: int) -> bool:
    """Check if the entered value is include in the entered range"""
    return True if entered_item.isdigit() and min_range <= int(entered_item) <= max_range else False


def validation_choose_account(entered_item: str, accounts: dict) -> bool:
    """Check if entered value is digit and include in accounts"""
    return True if entered_item.isdigit() and int(entered_item) in accounts else False


def validation_file_name(entered_item: str):
    """Check if enterd filename contains only legal characters"""
    if not entered_item:
        return False
    for letter in entered_item:
        if letter in r'/\:*?"<>|':
            return False
    return True


def validation_file_path(entered_item: str):
    """Check if entered path exist"""
    return True if path.exists(entered_item) else False


def validation_datetime(entered_item: str):
    """Check if entered string can be a datetime"""
    try:
        return datetime.fromisoformat(entered_item)
    except ValueError:
        return False


def get_answer(function: Callable, description: str, wrong_answer: str, args: tuple = None) -> str:
    """Check the validation of the entered element on the basis of the entered validation function"""
    def get_tuple():
        return (entered_answer,) if not args else tuple([x for x in [entered_answer] + [x for x in args]])
    while True:
        entered_answer = input(description)
        if function(*get_tuple()):
            return entered_answer
        else:
            print(wrong_answer)
