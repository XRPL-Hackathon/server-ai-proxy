from typing import Optional
from pymongo.collection import Collection
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timezone


class CategoryRecommendationRepository:
    def __init__(self, client: MongoClient):
        self.db = client.get_database()
        self.collection: Collection = self.db.get_collection('category_recommendations')

    def create_recommendation_request(self, file_id: str, user_id: str) -> dict:
        document = {
            "file_id": file_id,
            "user_id": user_id,
            "is_completed": False,
            "created_at": self.get_current_time()
        }
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    def get_recommendation_by_id(self, request_id: str, user_id: str) -> Optional[dict]:
        try:
            object_id = ObjectId(request_id)
            return self.collection.find_one({
                "_id": object_id,
                "user_id": user_id
            })
        except:
            return None

    def update_recommendation_result(self, request_id: str, predicted_category: str) -> Optional[dict]:
        try:
            object_id = ObjectId(request_id)
            result = self.collection.update_one(
                {"_id": object_id},
                {
                    "$set": {
                        "is_completed": True,
                        "predicted_category": predicted_category,
                        "updated_at": self.get_current_time()
                    }
                }
            )
            
            if result.modified_count == 0:
                return None
                
            return self.collection.find_one({"_id": object_id})
        except:
            return None
        
    def get_current_time(self):
        return datetime.now(timezone.utc) 