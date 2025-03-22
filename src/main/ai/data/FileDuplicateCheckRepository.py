from bson import ObjectId
from datetime import datetime, timezone


class FileDuplicateCheckRepository:
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.db = mongo_client.get_database()
        self.file_checks_collection = self.db.get_collection("file_duplicate_checks")
        self.files_collection = self.db.get_collection("files")
        self.file_embeddings_collection = self.db.get_collection("file_embeddings")
    
    def get_current_time(self):
        """현재 시간을 UTC 기준으로 반환합니다."""
        return datetime.now(timezone.utc)
    
    def get_file_by_id(self, file_id: str):
        """파일 ID로 파일 정보를 조회합니다."""
        try:
            file_obj_id = ObjectId(file_id)
            return self.files_collection.find_one({"_id": file_obj_id})
        except Exception as e:
            return None
    
    def has_file_embedding(self, file_id: str) -> bool:
        """파일의 임베딩 존재 여부를 확인합니다."""
        try:
            file_obj_id = ObjectId(file_id)
            result = self.file_embeddings_collection.find_one({"file_id": file_obj_id})
            return result is not None
        except Exception as e:
            return False
    
    def create_duplicate_check_request(self, file_id: str, user_id: str):
        """중복 검사 요청을 생성합니다."""
        now = self.get_current_time()
        document = {
            "file_id": file_id,
            "user_id": user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": now
        }
        
        result = self.file_checks_collection.insert_one(document)
        
        return self.file_checks_collection.find_one({"_id": result.inserted_id})
    
    def get_duplicate_check_by_file_id(self, file_id: str, user_id: str):
        """파일 ID와 사용자 ID로 중복 검사 요청을 조회합니다."""
        return self.file_checks_collection.find_one({
            "file_id": file_id,
            "user_id": user_id
        })
    
    def get_duplicate_check_by_id(self, request_id: str):
        """요청 ID로 중복 검사 요청을 조회합니다."""
        try:
            request_obj_id = ObjectId(request_id)
            return self.file_checks_collection.find_one({"_id": request_obj_id})
        except Exception as e:
            return None
    
    def update_file_duplicate_status(self, file_id: str, is_duplicated: bool):
        """파일의 중복 상태를 업데이트합니다."""
        try:
            file_obj_id = ObjectId(file_id)
            result = self.files_collection.update_one(
                {"_id": file_obj_id},
                {"$set": {"is_duplicated": is_duplicated}}
            )
            
            if result.modified_count > 0:
                return self.files_collection.find_one({"_id": file_obj_id})
            return None
        except Exception as e:
            return None
    
    def update_duplicate_check_result(self, request_id: str, is_duplicated: bool):
        """중복 검사 결과를 업데이트합니다."""
        try:
            now = self.get_current_time()
            request_obj_id = ObjectId(request_id)
            
            result = self.file_checks_collection.update_one(
                {"_id": request_obj_id},
                {
                    "$set": {
                        "is_completed": True,
                        "is_duplicated": is_duplicated,
                        "updated_at": now
                    }
                }
            )
            
            if result.modified_count > 0:
                return self.file_checks_collection.find_one({"_id": request_obj_id})
            return None
        except Exception as e:
            return None 