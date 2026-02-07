from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from sqlmodel import Session, select
from uuid import UUID


class BaseService(ABC):
    """
    Base service class providing common CRUD operations
    """
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def create(self, db: Session, obj_in: Dict[str, Any]):
        """
        Create a new record
        """
        db_obj = self.model_class(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: UUID):
        """
        Get a record by ID
        """
        statement = select(self.model_class).where(self.model_class.id == id)
        return db.exec(statement).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        """
        Get multiple records with pagination
        """
        statement = select(self.model_class).offset(skip).limit(limit)
        return db.exec(statement).all()
    
    def update(self, db: Session, db_obj, obj_in: Dict[str, Any]):
        """
        Update a record
        """
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, id: UUID):
        """
        Remove a record by ID
        """
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj