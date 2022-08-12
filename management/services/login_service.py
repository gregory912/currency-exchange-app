from management.security.security import Security
from management.services.common import *
from database.repository.crud_repo import CrudRepo
from database.model.tables import UserDataTable


class LoginService:
    def __init__(self, engine):
        self.engine = engine

        self.user_data_crud_repo = CrudRepo(self.engine, UserDataTable)

    def create_account(self):
        """Create an account for the new user"""
        print(f'{" " * 12}Would you like to create an account?')
        response = get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        if response == 'Y':
            while True:
                login = get_answer(
                    validation_alnum_and_not_digit,
                    'Enter login: ',
                    'Entered data contains illegal characters. Try again: ')
                password = Security.encode(Security(), get_answer(
                    validation_alnum_and_not_digit,
                    'Enter Password: ',
                    'Entered data contains illegal characters. Try again: '))
                if self.user_data_crud_repo.find_first_with_condition((UserDataTable.login, login)):
                    print(f'{" " * 12}Entered login is already used. Enter another login.')
                else:
                    break
            print('Enter user data:')
            name = get_answer(
                validation_alpha,
                'Enter your name: ',
                'Entered data contains illegal characters. Try again: ')
            surname = get_answer(
                validation_alpha,
                'Enter your surname: ',
                'Entered data contains illegal characters. Try again: ')
            country = get_answer(
                validation_alpha,
                'Enter the country where you come from: ',
                'Entered data contains illegal characters. Try again: ')
            address = get_answer(
                validation_space_or_alpha_not_digit,
                'Enter your address: ',
                'Entered data contains illegal characters. Try again: ')
            email = get_answer(
                validation_email,
                'Enter your email: ',
                'Entered data contains illegal characters. Try again: ')
            phone = get_answer(
                validation_digit,
                'Enter your phone: ',
                'Entered number should contain between 9 and 11 characters. Try again: ',
                (9, 11))
            main_currency = choose_currency("Choose the main currency for your account: ")
            self.user_data_crud_repo.add(
                name=name, surname=surname, country=country,
                address=address, email=email, phone=phone,
                login=login, password=password, creation_date=datetime.now(),
                main_currency=main_currency)
            print(f'{" " * 12}Your account has been created')
        else:
            raise SystemExit(0)

    def login(self):
        """Enter user data into the database. Encrypt the entered password"""
        while True:
            login = input('Enter your login: ')
            password = input('Enter your password: ')
            logged_in_user = self.user_data_crud_repo.find_first_with_condition((UserDataTable.login, login))
            if logged_in_user and Security.check_password(password, logged_in_user.password):
                print(f'\n{" " * 12}Welcome in your currency exchange account.')
                return logged_in_user
            else:
                print(f'{" " * 12}Account not found for the given data. Try again.')

    @staticmethod
    def does_account_exist():
        """Ask if the user already has an account"""
        print(f"{' ' * 12}Do you have a bank account?")
        response = get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        return True if response == 'Y' else False
