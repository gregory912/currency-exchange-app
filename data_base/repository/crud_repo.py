import inflection
from typing import List
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import between


class CrudRepo:
    def __init__(self, engine, entity_type):
        self._engine = engine
        self._base = declarative_base()
        self._entity_type = entity_type

    def _table_name(self):
        """Prepare the column name for insertion into the database"""
        return inflection.tableize(self._entity_type.__name__)

    def _create_session(self):
        """Create a new session"""
        return sessionmaker(self._engine, future=True)

    def add(self, **kwargs):
        """Add one row to the indicated database"""
        with self._engine.begin() as conn:
            item_to_add = insert(self._entity_type).values(kwargs)
            conn.execute(item_to_add)

    def add_join(self, item):
        """Add one row to the indicated database"""
        Session = self._create_session()
        with Session() as session:
            session.add_card(item)
            session.commit()

    def update_by_id(self, item_id: int, **kwargs):
        """Update the row data for the entered id_"""
        with self._engine.begin() as conn:
            item_to_add = update(self._entity_type).where(self._entity_type.id == item_id).values(kwargs)
            conn.execute(item_to_add)

    def find_by_id(self, item_id: int):
        """Find items by id_"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(self._entity_type.id == item_id)).first()
            return result

    def find_by_id_choose_columns(self, item_id: int, columns: tuple):
        """Find items by id_"""
        with self._engine.begin() as conn:
            result = conn.execute(select(columns).where(self._entity_type.id == item_id)).first()
            return result

    def find_all_by_id(self, item_ids: List[int]):
        """Return rows based on the list with the entered ids"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(self._entity_type.id.in_(item_ids))).all()
            return result

    def find_all(self):
        """Returns all rows for the given table"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type))
            return [item for item in result]

    def find_all_with_condition(self, condition: tuple) -> List[tuple]:
        """Find all items which comply the condition"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(condition[0] == condition[1]))
            return [item for item in result]

    def find_first_with_condition(self, condition: tuple):
        """Find first item which comply the condition"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(condition[0] == condition[1])).first()
            return result

    def find_between(self, elements: tuple) -> List[tuple]:
        """Find all items between indicated elements"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(between(*elements)))
            return [item for item in result]

    def get_last_row(self):
        """Return the last row"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).order_by(self._entity_type.id.desc())).first()
            return result

    def delete_by_id(self, item_id: int):
        """Delete the row for the entered id_"""
        with self._engine.begin() as conn:
            item_to_add = delete(self._entity_type).where(self._entity_type.id == item_id)
            conn.execute(item_to_add)

    def delete_all_by_id(self, items_id: List[int]):
        """Delete the rows for the entered ids"""
        with self._engine.begin() as conn:
            item_to_add = delete(self._entity_type).where(self._entity_type.id.in_(items_id))
            conn.execute(item_to_add)

    def join(self, item, columns: tuple):
        """Join columns for the given tables"""
        with self._engine.begin() as conn:
            result = conn.execute(select(columns).join(item)).all()
            return [item for item in result]

    def join_with_condition(self, item, columns: tuple, condition: tuple):
        """Join columns for the given tables. Return elements for the given elements"""
        with self._engine.begin() as conn:
            result = conn.execute(select(columns).join(item).where(condition[0] == condition[1])).all()
            return [item for item in result]
