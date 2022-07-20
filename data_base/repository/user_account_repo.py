from data_base.repository.crud_repo import CrudRepo
from sqlalchemy import select, and_, between


class UserAccountRepo(CrudRepo):
    def check_if_account_exist(self, id_user_data: int, currency: str):
        """Check if the account for the entered user and currency already exists"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(
                and_(self._entity_type.id_user_data == id_user_data, self._entity_type.currency == currency))).first()
            return result

    def find_btwn_dates(self, elements: tuple):
        """Return all items that are between the indicated dates and for the given account"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(
                and_(between(elements[0], elements[1], elements[2])), (elements[3] == elements[4])))
            return [item for item in result]
