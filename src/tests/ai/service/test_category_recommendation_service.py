import pytest
import uuid
from unittest.mock import MagicMock, patch
from bson import ObjectId
from datetime import datetime, timezone

from src.main.ai.service.CategoryRecommendationService import CategoryRecommendationService
from src.main.ai.models.CategoryRecommendation import (
    CategoryRecommendationRequest,
    CategoryRecommendationResponse,
    CategoryRecommendationStatusResponse,
    CategoryRecommendationResultRequest
)


class TestCategoryRecommendationService:
    def setup_method(self):
        # 목업 리포지토리 및 큐 생성
        self.mock_repository = MagicMock()
        self.mock_queue = MagicMock()
        
        # 테스트 대상 서비스 생성
        self.service = CategoryRecommendationService(self.mock_repository, self.mock_queue)
        
        # 테스트 공통 데이터
        self.test_file_id = "67dd86ac60a0a6d929904d47"
        self.test_user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        self.test_request_id = "6123456789abcdef01234567"
        self.test_object_id = ObjectId(self.test_request_id)
    
    def test_create_recommendation_request(self):
        # given
        request = CategoryRecommendationRequest(file_id=self.test_file_id)
        
        # 리포지토리 응답 설정
        mongo_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": str(self.test_user_id),
            "is_completed": False,
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc)
        }
        self.mock_repository.create_recommendation_request.return_value = mongo_document
        
        # when
        result = self.service.create_recommendation_request(request, self.test_user_id)
        
        # then
        self.mock_repository.create_recommendation_request.assert_called_once_with(
            file_id=self.test_file_id,
            user_id=str(self.test_user_id)
        )
        
        self.mock_queue.send_message.assert_called_once_with(
            request_id=self.test_request_id,
            file_id=self.test_file_id,
            user_id=str(self.test_user_id)
        )
        
        assert isinstance(result, CategoryRecommendationResponse)
        assert result.request_id == self.test_request_id
    
    def test_get_recommendation_status_exists(self):
        # given
        # 리포지토리 응답 설정 - 완료되지 않은 추천
        mongo_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": str(self.test_user_id),
            "is_completed": False,
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc)
        }
        self.mock_repository.get_recommendation_by_id.return_value = mongo_document
        
        # when
        result = self.service.get_recommendation_status(self.test_request_id, self.test_user_id)
        
        # then
        self.mock_repository.get_recommendation_by_id.assert_called_once_with(
            self.test_request_id, str(self.test_user_id)
        )
        
        assert isinstance(result, CategoryRecommendationStatusResponse)
        assert result.request_id == self.test_request_id
        assert result.is_completed is False
        assert result.predicted_category is None
    
    def test_get_recommendation_status_completed(self):
        # given
        # 리포지토리 응답 설정 - 완료된 추천
        mongo_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": str(self.test_user_id),
            "is_completed": True,
            "predicted_category": "기술",
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2023, 1, 2, tzinfo=timezone.utc)
        }
        self.mock_repository.get_recommendation_by_id.return_value = mongo_document
        
        # when
        result = self.service.get_recommendation_status(self.test_request_id, self.test_user_id)
        
        # then
        self.mock_repository.get_recommendation_by_id.assert_called_once_with(
            self.test_request_id, str(self.test_user_id)
        )
        
        assert isinstance(result, CategoryRecommendationStatusResponse)
        assert result.request_id == self.test_request_id
        assert result.is_completed is True
        assert result.predicted_category == "기술"
    
    def test_get_recommendation_status_not_found(self):
        # given
        # 리포지토리 응답 설정 - 문서 없음
        self.mock_repository.get_recommendation_by_id.return_value = None
        
        # when
        result = self.service.get_recommendation_status(self.test_request_id, self.test_user_id)
        
        # then
        self.mock_repository.get_recommendation_by_id.assert_called_once_with(
            self.test_request_id, str(self.test_user_id)
        )
        
        assert result is None
    
    def test_update_recommendation_result_success(self):
        # given
        request = CategoryRecommendationResultRequest(predicted_category="기술")
        
        # 리포지토리 응답 설정
        updated_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": str(self.test_user_id),
            "is_completed": True,
            "predicted_category": "기술",
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2023, 1, 2, tzinfo=timezone.utc)
        }
        self.mock_repository.update_recommendation_result.return_value = updated_document
        
        # when
        result = self.service.update_recommendation_result(self.test_request_id, request)
        
        # then
        self.mock_repository.update_recommendation_result.assert_called_once_with(
            request_id=self.test_request_id,
            predicted_category=request.predicted_category
        )
        
        assert isinstance(result, CategoryRecommendationStatusResponse)
        assert result.request_id == self.test_request_id
        assert result.is_completed is True
        assert result.predicted_category == "기술"
    
    def test_update_recommendation_result_not_found(self):
        # given
        request = CategoryRecommendationResultRequest(predicted_category="기술")
        
        # 리포지토리 응답 설정 - 업데이트 실패
        self.mock_repository.update_recommendation_result.return_value = None
        
        # when
        result = self.service.update_recommendation_result(self.test_request_id, request)
        
        # then
        self.mock_repository.update_recommendation_result.assert_called_once_with(
            request_id=self.test_request_id,
            predicted_category=request.predicted_category
        )
        
        assert result is None 