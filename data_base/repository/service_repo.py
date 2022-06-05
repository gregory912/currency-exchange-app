from data_base.repository.crud_repo import CrudRepo
from sqlalchemy import select


class ServiceRepo(CrudRepo):
    def find_service(self, entity_id: int):
        """Find items by id"""
        with self._engine.begin() as conn:
            result = conn.execute(select(self._entity_type).where(self._entity_type.id_user_data == entity_id)).first()
            return result
