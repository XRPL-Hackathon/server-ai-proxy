from typing import Optional
from pymongo.collection import Collection
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timezone


class FileDuplicateCheckRepository:
    def __init__(self, client: MongoClient):
        self.db = client.get_database()
        self.collection: Collection = self.db.get_collection('file_duplicate_checks')
        self.files_collection: Collection = self.db.get_collection('files')

    def create_duplicate_check_request(self, file_id: str, user_id: str) -> dict:
        document = {
            "file_id": file_id,
            "user_id": user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.get_current_time()
        }
        result = self.collection.insert_one(document)
        document = document.copy()
        document["_id"] = result.inserted_id
        return document

    def get_duplicate_check_by_id(self, request_id: str) -> Optional[dict]:
        try:
            object_id = ObjectId(request_id)
            return self.collection.find_one({"_id": object_id})
        except:
            return None

    def get_duplicate_check_by_file_id(self, file_id: str, user_id: str) -> Optional[dict]:
        try:
            return self.collection.find_one({
                "file_id": file_id,
                "user_id": user_id
            })
        except:
            return None

    def update_duplicate_check_result(self, request_id: str, is_duplicated: bool) -> Optional[dict]:
        try:
            object_id = ObjectId(request_id)
            result = self.collection.update_one(
                {"_id": object_id},
                {
                    "$set": {
                        "is_completed": True,
                        "is_duplicated": is_duplicated,
                        "updated_at": self.get_current_time()
                    }
                }
            )
            
            if result.modified_count == 0:
                return None
                
            return self.collection.find_one({"_id": object_id})
        except:
            return None

    def get_file_by_id(self, file_id: str) -> Optional[dict]:
        try:
            object_id = ObjectId(file_id)
            return self.files_collection.find_one({"_id": object_id})
        except:
            return None
        
    def get_current_time(self):
        return datetime.now(timezone.utc) 