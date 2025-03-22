import pytest
from unittest.mock import MagicMock, patch, ANY
from bson import ObjectId
from datetime import datetime, timezone
from src.main.ai.data.CategoryRecommendationRepository import CategoryRecommendationRepository


class TestCategoryRecommendationRepository:
    def setup_method(self):
        # 목업 MongoDB 클라이언트 생성
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        
        # 클라이언트에서 DB와 컬렉션 반환하도록 설정
        self.mock_client.get_database.return_value = self.mock_db
        self.mock_db.get_collection.return_value = self.mock_collection
        
        # 테스트 대상 리포지토리 생성
        self.repository = CategoryRecommendationRepository(self.mock_client)
        
        # 현재 시간을 일정하게 만들기 위한 패치
        self.time_patcher = patch.object(
            self.repository, 'get_current_time', 
            return_value=datetime(2023, 1, 1, tzinfo=timezone.utc)
        )
        self.mock_time = self.time_patcher.start()
    
    def teardown_method(self):
        # 패치 제거
        self.time_patcher.stop()
    
    def test_create_recommendation_request(self):
        # given
        file_id = "67dd86ac60a0a6d929904d47"
        user_id = "test-user-id"
        mock_id = ObjectId("6123456789abcdef01234567")
        
        # MongoDB insert_one의 응답 설정
        self.mock_collection.insert_one.return_value = MagicMock(inserted_id=mock_id)
        
        # when
        result = self.repository.create_recommendation_request(file_id, user_id)
        
        # then
        expected_doc = {
            "file_id": file_id,
            "user_id": user_id,
            "is_completed": False,
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "_id": mock_id
        }
        
        # ANY를 사용하여 document의 내용을 확인하지 않고 호출 자체만 확인
        self.mock_collection.insert_one.assert_called_once()
        assert result == expected_doc
    
    def test_get_recommendation_by_id(self):
        # given
        request_id = "6123456789abcdef01234567"
        user_id = "test-user-id"
        expected_result = {
            "_id": ObjectId(request_id),
            "file_id": "67dd86ac60a0a6d929904d47",
            "user_id": user_id,
            "is_completed": False,
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc)
        }
        
        self.mock_collection.find_one.return_value = expected_result
        
        # when
        result = self.repository.get_recommendation_by_id(request_id, user_id)
        
        # then
        self.mock_collection.find_one.assert_called_once_with({
            "_id": ObjectId(request_id),
            "user_id": user_id
        })
        assert result == expected_result
    
    def test_get_recommendation_by_id_invalid_id(self):
        # given
        request_id = "invalid-id"
        user_id = "test-user-id"
        
        # when
        result = self.repository.get_recommendation_by_id(request_id, user_id)
        
        # then
        assert result is None
        self.mock_collection.find_one.assert_not_called()
    
    def test_update_recommendation_result(self):
        # given
        request_id = "6123456789abcdef01234567"
        predicted_category = "기술"
        
        # MongoDB 응답 설정
        update_result = MagicMock(modified_count=1)
        self.mock_collection.update_one.return_value = update_result
        
        expected_doc = {
            "_id": ObjectId(request_id),
            "file_id": "67dd86ac60a0a6d929904d47",
            "user_id": "test-user-id",
            "is_completed": True,
            "predicted_category": predicted_category,
            "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc)
        }
        self.mock_collection.find_one.return_value = expected_doc
        
        # when
        result = self.repository.update_recommendation_result(request_id, predicted_category)
        
        # then
        self.mock_collection.update_one.assert_called_once_with(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "is_completed": True,
                    "predicted_category": predicted_category,
                    "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc)
                }
            }
        )
        self.mock_collection.find_one.assert_called_once_with({"_id": ObjectId(request_id)})
        assert result == expected_doc
    
    def test_update_recommendation_result_invalid_id(self):
        # given
        request_id = "invalid-id"
        predicted_category = "기술"
        
        # when
        result = self.repository.update_recommendation_result(request_id, predicted_category)
        
        # then
        assert result is None
        self.mock_collection.update_one.assert_not_called()
        self.mock_collection.find_one.assert_not_called()
    
    def test_update_recommendation_result_not_found(self):
        # given
        request_id = "6123456789abcdef01234567"
        predicted_category = "기술"
        
        # MongoDB 응답 설정 - modified_count가 0이면 업데이트된 문서가 없음
        update_result = MagicMock(modified_count=0)
        self.mock_collection.update_one.return_value = update_result
        
        # when
        result = self.repository.update_recommendation_result(request_id, predicted_category)
        
        # then
        self.mock_collection.update_one.assert_called_once()
        self.mock_collection.find_one.assert_not_called()
        assert result is None 