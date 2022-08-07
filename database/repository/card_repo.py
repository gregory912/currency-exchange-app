from database.repository.crud_repo import CrudRepo
from database.model.tables import CardTable, CardTransactionTable
from sqlalchemy import select, and_, between
from database.repository.common import *


class CardRepo(CrudRepo):
    def join_cards(self, item, card_type: str, id_user_data: int):
        """Return elements for entered card_type and user id"""
        with self._engine.begin() as conn:
            result = conn.execute(select(CardTable.id).join(item).where(
                and_(CardTable.card_type == card_type, CardTable.id_user_data == id_user_data))).all()
            return [item for item in result]

    def find_all_cards(self, id_user_data: int) -> list[tuple]:
        """Find all cards for entered user"""
        with self._engine.begin() as conn:
            result = conn.execute(select(
                self._entity_type.id,
                self._entity_type.card_number,
                self._entity_type.valid_thru,
                self._entity_type.card_name,
                self._entity_type.card_type,
                self._entity_type.main_currency).where(CardTable.id_user_data == id_user_data))
            return [item for item in result]

    def get_monthly_card_trans_for_user(self, logged_in_user: int) -> list[tuple]:
        """Get all card transactions for a given user"""
        with self._engine.begin() as conn:
            result = conn.execute(
                select(CardTransactionTable.amount_in_main_user_currency).
                join(CardTable).
                where(
                    and_(
                        between(
                            CardTransactionTable.transaction_time, fst_day_of_this_month(), fst_day_of_next_month())),
                    and_((logged_in_user == CardTable.id_user_data),
                         CardTransactionTable.transaction_type == "Withdrawals ATM")))
            return [item for item in result]
