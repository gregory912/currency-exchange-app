from data_base.repository.crud_repo import CrudRepo
from sqlalchemy import select, and_, between
from data_base.model.tables import CurrencyExchangeTable, UserAccountTable
from data_base.repository.common import *


class UserAccountRepo(CrudRepo):
    def check_if_account_exist(self, id_user_data: int, currency: str):
        """Check if the account for the entered user and currency already exists"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(
                and_(self._entity_type.id_user_data == id_user_data, self._entity_type.currency == currency))).first()
            return result

    def find_btwn_dates(self, elements: tuple) -> list[tuple]:
        """Return all items that are between the indicated dates and for the given account"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(
                and_(between(elements[0], elements[1], elements[2])), (elements[3] == elements[4])))
            return [item for item in result]

    def get_monthly_exchanges_for_user(self, logged_in_user: int) -> list[tuple]:
        """Get all currency exchange transactions for one user"""
        with self._engine.begin() as conn:
            result = conn.execute(
                select(
                    UserAccountTable.id, CurrencyExchangeTable.id, CurrencyExchangeTable.amount_in_main_user_currency).
                join(CurrencyExchangeTable, UserAccountTable.id == CurrencyExchangeTable.id_user_account_out).
                where(
                    and_(
                        between(
                            CurrencyExchangeTable.transaction_time, fst_day_of_this_month(), fst_day_of_next_month())),
                        (logged_in_user == UserAccountTable.id_user_data)))
            return [item for item in result]
