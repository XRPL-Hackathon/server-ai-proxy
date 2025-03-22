import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from datetime import datetime, timezone

from src.main.ai.data.FileDuplicateCheckRepository import FileDuplicateCheckRepository


class TestFileDuplicateCheckRepository:
    def setup_method(self):
        # 목업 MongoDB 클라이언트 생성
        self.mock_collection = MagicMock()
        self.mock_files_collection = MagicMock()
        self.mock_db = MagicMock()
        self.mock_db.get_collection.side_effect = lambda name: self.mock_collection if name == 'file_duplicate_checks' else self.mock_files_collection
        
        self.mock_client = MagicMock()
        self.mock_client.get_database.return_value = self.mock_db
        
        # 테스트 대상 레포지토리 생성
        self.repository = FileDuplicateCheckRepository(self.mock_client)
        
        # 테스트 공통 데이터
        self.test_file_id = "6123456789abcdef01234567"
        self.test_user_id = "12345678-1234-5678-1234-567812345678"
        self.test_request_id = "7123456789abcdef01234567"
        self.test_object_id = ObjectId(self.test_request_id)
        self.test_file_object_id = ObjectId(self.test_file_id)
        self.test_time = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        # 시간 고정을 위한 패치
        self.time_patch = patch.object(self.repository, 'get_current_time', return_value=self.test_time)
        self.time_patch.start()
    
    def teardown_method(self):
        self.time_patch.stop()
    
    def test_create_duplicate_check_request(self):
        # given
        expected_document = {
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.test_time
        }
        self.mock_collection.insert_one.return_value.inserted_id = self.test_object_id
        
        # when
        result = self.repository.create_duplicate_check_request(self.test_file_id, self.test_user_id)
        
        # then
        self.mock_collection.insert_one.assert_called_once_with(expected_document)
        assert result["_id"] == self.test_object_id
        assert result["file_id"] == self.test_file_id
        assert result["user_id"] == self.test_user_id
        assert result["is_completed"] == False
        assert result["is_duplicated"] is None
        assert result["created_at"] == self.test_time
    
    def test_get_duplicate_check_by_id_found(self):
        # given
        expected_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.test_time
        }
        self.mock_collection.find_one.return_value = expected_document
        
        # when
        result = self.repository.get_duplicate_check_by_id(self.test_request_id)
        
        # then
        self.mock_collection.find_one.assert_called_once_with({"_id": self.test_object_id})
        assert result == expected_document
    
    def test_get_duplicate_check_by_id_not_found(self):
        # given
        self.mock_collection.find_one.return_value = None
        
        # when
        result = self.repository.get_duplicate_check_by_id(self.test_request_id)
        
        # then
        self.mock_collection.find_one.assert_called_once_with({"_id": self.test_object_id})
        assert result is None
    
    def test_get_duplicate_check_by_id_invalid_id(self):
        # given
        # ObjectId 변환 실패
        
        # when
        result = self.repository.get_duplicate_check_by_id("invalid_id")
        
        # then
        self.mock_collection.find_one.assert_not_called()
        assert result is None
    
    def test_get_duplicate_check_by_file_id_found(self):
        # given
        expected_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.test_time
        }
        self.mock_collection.find_one.return_value = expected_document
        
        # when
        result = self.repository.get_duplicate_check_by_file_id(self.test_file_id, self.test_user_id)
        
        # then
        self.mock_collection.find_one.assert_called_once_with({
            "file_id": self.test_file_id,
            "user_id": self.test_user_id
        })
        assert result == expected_document
    
    def test_get_duplicate_check_by_file_id_not_found(self):
        # given
        self.mock_collection.find_one.return_value = None
        
        # when
        result = self.repository.get_duplicate_check_by_file_id(self.test_file_id, self.test_user_id)
        
        # then
        self.mock_collection.find_one.assert_called_once_with({
            "file_id": self.test_file_id,
            "user_id": self.test_user_id
        })
        assert result is None
    
    def test_update_duplicate_check_result_success(self):
        # given
        # 업데이트 성공
        self.mock_collection.update_one.return_value.modified_count = 1
        
        expected_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": True,
            "is_duplicated": False,
            "created_at": self.test_time,
            "updated_at": self.test_time
        }
        self.mock_collection.find_one.return_value = expected_document
        
        # when
        result = self.repository.update_duplicate_check_result(self.test_request_id, False)
        
        # then
        self.mock_collection.update_one.assert_called_once_with(
            {"_id": self.test_object_id},
            {
                "$set": {
                    "is_completed": True,
                    "is_duplicated": False,
                    "updated_at": self.test_time
                }
            }
        )
        self.mock_collection.find_one.assert_called_once_with({"_id": self.test_object_id})
        assert result == expected_document
    
    def test_update_duplicate_check_result_not_found(self):
        # given
        # 업데이트 실패
        self.mock_collection.update_one.return_value.modified_count = 0
        
        # when
        result = self.repository.update_duplicate_check_result(self.test_request_id, False)
        
        # then
        self.mock_collection.update_one.assert_called_once()
        self.mock_collection.find_one.assert_not_called()
        assert result is None
    
    def test_update_duplicate_check_result_invalid_id(self):
        # given
        # ObjectId 변환 실패
        
        # when
        result = self.repository.update_duplicate_check_result("invalid_id", False)
        
        # then
        self.mock_collection.update_one.assert_not_called()
        self.mock_collection.find_one.assert_not_called()
        assert result is None
    
    def test_get_file_by_id_found(self):
        # given
        expected_document = {
            "_id": self.test_file_object_id,
            "file_key": "example.pdf",
            "s3_url": "https://bucket.s3.amazonaws.com/example.pdf"
        }
        self.mock_files_collection.find_one.return_value = expected_document
        
        # when
        result = self.repository.get_file_by_id(self.test_file_id)
        
        # then
        self.mock_files_collection.find_one.assert_called_once_with({"_id": self.test_file_object_id})
        assert result == expected_document
    
    def test_get_file_by_id_not_found(self):
        # given
        self.mock_files_collection.find_one.return_value = None
        
        # when
        result = self.repository.get_file_by_id(self.test_file_id)
        
        # then
        self.mock_files_collection.find_one.assert_called_once_with({"_id": self.test_file_object_id})
        assert result is None
    
    def test_get_file_by_id_invalid_id(self):
        # given
        # ObjectId 변환 실패
        
        # when
        result = self.repository.get_file_by_id("invalid_id")
        
        # then
        self.mock_files_collection.find_one.assert_not_called()
        assert result is None 