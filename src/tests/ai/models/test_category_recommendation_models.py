import pytest
import uuid
from pydantic import ValidationError

from src.main.ai.models.CategoryRecommendation import (
    CategoryRecommendationRequest,
    CategoryRecommendationResponse,
    CategoryRecommendationStatusResponse,
    CategoryRecommendationResultRequest
)


class TestCategoryRecommendationModels:
    def test_category_recommendation_request_valid(self):
        # given
        file_id = "67dd86ac60a0a6d929904d47"
        
        # when
        model = CategoryRecommendationRequest(file_id=file_id)
        
        # then
        assert model.file_id == file_id
    
    def test_category_recommendation_request_invalid(self):
        # when/then - 파일 ID가 없는 경우 검증 오류
        with pytest.raises(ValidationError):
            CategoryRecommendationRequest()
    
    def test_category_recommendation_response(self):
        # given
        request_id = "test-request-id"
        
        # when
        model = CategoryRecommendationResponse(request_id=request_id)
        
        # then
        assert model.request_id == request_id
    
    def test_category_recommendation_response_default_id(self):
        # when
        model = CategoryRecommendationResponse()
        
        # then
        assert model.request_id is not None
        # UUID 형식으로 변환 가능한지 확인
        uuid.UUID(model.request_id)
    
    def test_category_recommendation_status_response_incomplete(self):
        # given
        request_id = "test-request-id"
        
        # when
        model = CategoryRecommendationStatusResponse(
            request_id=request_id,
            is_completed=False
        )
        
        # then
        assert model.request_id == request_id
        assert model.is_completed is False
        assert model.predicted_category is None
    
    def test_category_recommendation_status_response_complete(self):
        # given
        request_id = "test-request-id"
        category = "기술"
        
        # when
        model = CategoryRecommendationStatusResponse(
            request_id=request_id,
            is_completed=True,
            predicted_category=category
        )
        
        # then
        assert model.request_id == request_id
        assert model.is_completed is True
        assert model.predicted_category == category
    
    def test_category_recommendation_result_request_valid(self):
        # given
        category = "기술"
        
        # when
        model = CategoryRecommendationResultRequest(predicted_category=category)
        
        # then
        assert model.predicted_category == category
    
    def test_category_recommendation_result_request_invalid(self):
        # when/then - 카테고리가 없는 경우 검증 오류
        with pytest.raises(ValidationError):
            CategoryRecommendationResultRequest() 