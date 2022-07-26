from data_base.repository.crud_repo import CrudRepo
from data_base.model.tables import CardTable
from sqlalchemy import select, and_


class CardRepo(CrudRepo):
    def join_cards(self, item, card_type: str, id_user_data: int):
        """Return elements for entered card_type and logged_in_user id"""
        with self._engine.begin() as conn:
            result = conn.execute(select(CardTable.id).join(item).where(
                and_(CardTable.card_type == card_type, CardTable.id_user_data == id_user_data))).all()
            return [item for item in result]

    def find_all_cards(self, id_user_data: int) -> list[tuple]:
        """Find all cards for entered logged_in_user"""
        with self._engine.begin() as conn:
            result = conn.execute(select(
                self._entity_type.id,
                self._entity_type.card_number,
                self._entity_type.valid_thru,
                self._entity_type.card_name,
                self._entity_type.card_type,
                self._entity_type.main_currency
            ).where(CardTable.id_user_data == id_user_data))
            return [item for item in result]
