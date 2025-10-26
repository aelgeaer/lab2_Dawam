from typing import List, Optional, Type, Any, Dict
from pymongo import MongoClient
from app.repositories.base import BaseRepository
import os

class MongoDBRepository(BaseRepository):
    def __init__(self, collection_name: str):
        self.client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
        self.db = self.client.news_db
        self.collection = self.db[collection_name]
    
    def create(self, obj_in: Any) -> Dict:
        obj_dict = obj_in.dict()
        result = self.collection.insert_one(obj_dict)
        obj_dict["id"] = str(result.inserted_id)
        return obj_dict
    
    def get(self, id: int) -> Optional[Dict]:
        return self.collection.find_one({"id": id})
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        return list(self.collection.find().skip(skip).limit(limit))
    
    def update(self, id: int, obj_in: Any) -> Optional[Dict]:
        update_data = obj_in.dict(exclude_unset=True)
        result = self.collection.update_one({"id": id}, {"$set": update_data})
        if result.modified_count:
            return self.get(id)
        return None
    
    def delete(self, id: int) -> bool:
        result = self.collection.delete_one({"id": id})
        return result.deleted_count > 0
