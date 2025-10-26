from typing import List, Optional, Type, Any
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models import Base

class SQLAlchemyRepository(BaseRepository):
    def __init__(self, db: Session, model: Type[Base]):
        self.db = db
        self.model = model
    
    def create(self, obj_in: Any) -> Base:
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get(self, id: int) -> Optional[Base]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Base]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: int, obj_in: Any) -> Optional[Base]:
        db_obj = self.db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        db_obj = self.db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
