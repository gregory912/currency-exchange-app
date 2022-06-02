import logging
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, sessionmaker
import inflection
from typing import List


class CrudRepo:

    def __init__(self, engine, entity_type):
        self._engine = engine
        self._base = declarative_base()
        self._entity_type = type(entity_type())

    def _create_session(self):
        return sessionmaker(bind=self._engine, expire_on_commit=False)

    def _table_name(self):
        return inflection.tableize(self._entity_type.__name__)

    def add_or_update(self, item):
        try:
            new_session = self._create_session()
            session = new_session()
            if item.id:
                item = session.merge(item)
            session.add(item)
            session.commit()
            logging.info('Item correctly inserted or updated into db')
            return item.id
        except Exception as e:
            logging.error(e)
            session.rollback()
        finally:
            session.close()

    def find_by_id(self, item_id):
        try:
            new_session = self._create_session()
            session = new_session()
            return session.query(self._entity_type).filter_by(id=item_id).first()
        except Exception as e:
            logging.error(e)
            session.rollback()
        finally:
            session.close()

    def find_all_by_id(self, item_ids):
        try:
            new_session = self._create_session()
            session = new_session()
            return session.query(self._entity_type).filter(self._entity_type.id.in_(item_ids)).all()
        except Exception as e:
            logging.error(e)
            session.rollback()
        finally:
            session.close()

    def find_all(self):
        try:
            new_session = self._create_session()
            session = new_session()
            return session.query(self._entity_type).all()
        except Exception as e:
            logging.error(e)
            session.rollback()
        finally:
            session.close()

    def delete_by_id(self, item_id):
        try:
            new_session = self._create_session()
            session = new_session()
            item_to_delete = session.query(self._entity_type).filter_by(id=item_id).first()
            if not item_to_delete:
                raise ValueError('Cannot delete item')
            session.delete(item_to_delete)
            session.commit()
            return item_to_delete.id
        except Exception as e:
            logging.error(e)
            session.rollback()
        finally:
            session.close()

    def delete_all_by_id(self, items_id: List[int]):
        try:
            new_session = self._create_session()
            session = new_session()
            statement = self._entity_type.__table__.delete().where(self._entity_type.id.in_(items_id))
            session.execute(statement)
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()
        finally:
            session.close()
