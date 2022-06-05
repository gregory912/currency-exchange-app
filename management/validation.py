import re
import os
from typing import Callable


class Validation:
    @staticmethod
    def validation_of_answer(entered_value: str) -> bool:
        """Check is the answer is y or n"""
        return False if entered_value != 'Y' and entered_value != 'N' else True

    @staticmethod
    def validation_alnum_and_not_digit(entered_value: str) -> bool:
        """Check if the entered value is alphanumeric and is not digits"""
        return True if entered_value.isalnum() and not entered_value.isdigit() else False

    @staticmethod
    def validation_alpha(entered_item: str) -> bool:
        """Check if the entered value contains only letters"""
        return True if entered_item.isalpha() else False

    @staticmethod
    def validation_digit(entered_item: str, min_length: int, max_length: int) -> bool:
        """Check if the entered value contains only digits"""
        return True if entered_item.isdigit() and min_length <= len(entered_item) <= max_length else False

    @staticmethod
    def validation_space_or_alpha_not_digit(entered_item: str) -> bool:
        """Check if the entered value contains space, letters"""
        if entered_item[:1] == ' ' or entered_item[-1:] == ' ':
            return False
        if entered_item.replace(' ', '').isdigit():
            return False
        for x in entered_item:
            if not (x == ' ' or x.isalnum()):
                return False
        return True

    @staticmethod
    def validation_decimal(entered_item: str) -> bool:
        """Check if the entered number is Decimal"""
        return True if re.match(r'\d+\.\d+', entered_item) or entered_item.isdigit() else False

    @staticmethod
    def validation_email(entered_item: str) -> bool:
        """Check if the value provided is an email address"""
        return True if re.match(r'^\S+@\S+\.\S+$', entered_item) else False

    @staticmethod
    def validation_chosen_operation(entered_item: str, min_range: int, max_range: int) -> bool:
        """Check if the entered value is include in the entered range"""
        return True if entered_item.isdigit() and min_range <= int(entered_item) <= max_range else False

    @staticmethod
    def validation_choose_account(entered_item: str, accounts: dict) -> bool:
        """Check if entered value is digit and include in accounts"""
        return True if entered_item.isdigit() and int(entered_item) in accounts else False

    @staticmethod
    def validation_file_name(entered_item: str):
        """Check if enterd filename contains only legal characters"""
        for letter in entered_item:
            if letter in r'/\:*?"<>|':
                return False
        return True

    @staticmethod
    def validation_file_path(entered_item: str):
        """Check if entered path exist"""
        return True if os.path.exists(entered_item) else False

    @staticmethod
    def get_answer(function: Callable, description: str, wrong_answer: str, args: tuple = None) -> str:
        """Check the validation of the entered element on the basis of the entered validation function"""
        def get_tuple():
            return (entered_answer,) if not args else tuple([x for x in [entered_answer] + [x for x in args] if x])
        while True:
            entered_answer = input(description)
            if function(*get_tuple()):
                return entered_answer
            else:
                print(wrong_answer)
