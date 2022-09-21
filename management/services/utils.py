from abc import ABC, abstractmethod
from management.security.security import Security
from management.services.common import *


class GetReply(ABC):
    @abstractmethod
    def get_value(self):
        pass


class GetReplyAnswer(GetReply):
    def get_value(self):
        return get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')


class GetReplyDoesAccountExist(GetReply):
    def get_value(self):
        print(f"{' ' * 12}Do you have a bank account?")
        return get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')


class GetReplyAnswerAccount(GetReply):
    def get_value(self):
        print(f'{" " * 12}Would you like to create an account?')
        return get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')


class GetReplyLogin(GetReply):
    def get_value(self):
        return get_answer(
            validation_alnum_and_not_digit,
            'Enter login: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyPassword(GetReply):
    def get_value(self):
        return Security.encode(Security(), get_answer(
            validation_alnum_and_not_digit,
            'Enter Password: ',
            'Entered data contains illegal characters. Try again: '))


class GetReplyName(GetReply):
    def get_value(self):
        return get_answer(
            validation_alpha,
            'Enter your name: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplySurname(GetReply):
    def get_value(self):
        return get_answer(
            validation_alpha,
            'Enter your surname: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyCountry(GetReply):
    def get_value(self):
        return get_answer(
            validation_alpha,
            'Enter the country where you come from: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyAddress(GetReply):
    def get_value(self):
        return get_answer(
            validation_space_or_alpha_not_digit,
            'Enter your address: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyEmail(GetReply):
    def get_value(self):
        return get_answer(
            validation_email,
            'Enter your email: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyPhone(GetReply):
    def get_value(self):
        return get_answer(
            validation_digit,
            'Enter your phone: ',
            'Entered number should contain between 9 and 11 characters. Try again: ',
            (9, 11))


class GetReplyUserWithoutAcc(GetReply):
    def get_value(self):
        print(f"{' ' * 12}You don't have any open account in the internet exchange currency. "
              f"Would you like to open a new account?")
        return get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')


class GetReplyUserTransferTitle(GetReply):
    def get_value(self):
        return get_answer(
            validation_space_or_alpha_not_digit,
            'Enter the transfer title: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyAmount(GetReply):
    def get_value(self):
        return get_answer(
            validation_decimal,
            'Enter the amount: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyPayerName(GetReply):
    def get_value(self):
        return get_answer(
            validation_space_or_alpha_not_digit,
            'Enter the payer name: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyPayerAccNumber(GetReply):
    def get_value(self):
        return get_answer(
            validation_digit,
            'Enter the payer account number: ',
            'Entered data is not correct. The number should contain between 20 - 26 digits. Try again: ',
            (20, 26))


class GetReplyCardName(GetReply):
    def get_value(self):
        return get_answer(
            validation_space_or_alpha_not_digit,
            'Enter the name of the card: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyLimit(GetReply):
    def get_value(self):
        return get_answer(
            validation_decimal,
            'Enter the new limit: ',
            'Entered data contains illegal characters. Try again: ')


class GetReplyCard(GetReply):
    def get_value(self):
        print(f"{' ' * 12}You don't have any card for your account. "
              f"Would you like to open a new account?")
        return get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')


class GetReplyPayerAccNb(GetReply):
    def get_value(self):
        return get_answer(
            validation_digit,
            'Enter the payer account number: ',
            'Entered data is not correct. The number should contain between 20 - 26 digits. Try again: ',
            (20, 26))


class GetReplyWithValue(ABC):
    @abstractmethod
    def get_value(self, value: list):
        pass


class GetReplyWithValueChosenAcc(GetReplyWithValue):
    def get_value(self, value: list):
        return get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, len(value)))


class GetReplyWithValueChosenAccCurExch(GetReplyWithValue):
    def get_value(self, value: list):
        return get_answer(
            validation_chosen_operation,
            'Select the currency for which you want to perform currency exchange: ',
            'Entered data contains illegal characters. Try again: ',
            (1, len(value)))


class GetReplyWithValueChosenCur(GetReplyWithValue):
    def get_value(self, value: int):
        return get_answer(
            validation_chosen_operation,
            'Enter chosen currency: ',
            'Entered data contains illegal characters. Try again: ',
            (1, value))


class GetReplyWithValueChosenLimit(GetReplyWithValue):
    def get_value(self, value: int):
        return get_answer(
            validation_chosen_operation,
            'Enter chosen limit type: ',
            'Entered data contains illegal characters. Try again: ',
            (1, value))
