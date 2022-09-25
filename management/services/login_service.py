from database.repository.crud_repo import CrudRepo
from database.model.tables import UserDataTable
from management.services.answers import *
from management.services.common import *


class Login:
    def __init__(self, engine):
        self.engine = engine

        self.user_data_crud_repo = CrudRepo(self.engine, UserDataTable)
        self.user = None

    def get_user(self):
        """For valid data, return the user"""
        while True:
            self._find_user()

            if self._check_security():
                print(f'\n{" " * 12}Welcome in your currency exchange account.')
                return self.user
            else:
                print(f'{" " * 12}Account not found for the given data. Try again.')

    def _find_user(self):
        """Find a user based on the entered login"""
        self.user = self.user_data_crud_repo.find_first_with_condition((UserDataTable.login, input('Enter your login: ')))

    def _check_security(self):
        """Check that the password entered matches the encrypted password in the database"""
        return Security.check_password(input('Enter your password: '), self.user.password)

    @staticmethod
    def does_account_exist():
        """Ask if the user already has an account"""
        return GetReplyDoesAccountExist().get_value() == 'Y'


class CreateAccount:
    def __init__(self, engine):
        self.engine = engine

        self.user_data_crud_repo = CrudRepo(self.engine, UserDataTable)

    def create_account(self):
        """Create an account for the new user"""
        login = self._get_login()
        password = GetReplyPassword().get_value()

        print('Enter user data:')
        name = GetReplyName().get_value()
        surname = GetReplySurname().get_value()
        country = GetReplyCountry().get_value()
        address = GetReplyAddress().get_value()
        email = GetReplyEmail().get_value()
        phone = GetReplyPhone().get_value()
        main_currency = choose_currency("Choose the main currency for your account: ")

        self.user_data_crud_repo.add(
            name=name, surname=surname, country=country,
            address=address, email=email, phone=phone,
            login=login, password=password, creation_date=datetime.now(),
            main_currency=main_currency)

        print(f'{" " * 12}Your account has been created')

    def _get_login(self):
        """Check that the login you entered is not already taken."""
        if GetReplyAnswerAccount().get_value() == 'Y':
            while True:
                login = GetReplyLogin().get_value()
                if self.user_data_crud_repo.find_first_with_condition((UserDataTable.login, login)):
                    print(f'{" " * 12}Entered login is already used. Enter another login.')
                else:
                    return login
        else:
            raise SystemExit(0)
