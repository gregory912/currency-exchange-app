from data_base.repository.crud_repo import CrudRepo
from sqlalchemy import select


class UserAccountRepo(CrudRepo):
    def find_account_number(self, account_number: str):
        """Check if the entered account number exists in the database"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(
                self._entity_type.account_number == account_number)).first()
            return result

    def check_if_account_exist(self, id_user_data: int, currency: str):
        """Check if the account for the entered user and currency already exists"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(
                self._entity_type.id_user_data == id_user_data, self._entity_type.currency == currency)).first()
            return result

    def find_all_accounts(self, id_user_data: int):
        """Find all accounts for the given user id number"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(
                self._entity_type.id_user_data == id_user_data)).all()
            return result
