from data_base.repository.crud_repo import CrudRepo
from sqlalchemy import select


class UserRepo(CrudRepo):
    def find_user(self, entity_login: str):
        """Find items by id"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(self._entity_type.login == entity_login)).first()
            return result
