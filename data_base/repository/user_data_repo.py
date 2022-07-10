from data_base.repository.crud_repo import CrudRepo
from sqlalchemy import select


class UserDataRepo(CrudRepo):
    def find_user_data(self, entity_id: str):
        """Find user data by id from user table"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(self._entity_type.id_user == entity_id)).first()
            return result

    def find_user(self, entity_login: str):
        """Find items by name"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(self._entity_type.login == entity_login)).first()
            return result
