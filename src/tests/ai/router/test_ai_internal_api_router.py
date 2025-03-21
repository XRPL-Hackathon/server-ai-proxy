import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.main.ai.models.CategoryRecommendation import CategoryRecommendationStatusResponse
from src.main.ai.router.AIInternalAPIRouter import router as internal_router


# 테스트용 앱 생성
app = FastAPI()
app.include_router(internal_router)

@pytest.fixture
def client():
    return TestClient(app)


class TestAIInternalAPIRouter:
    def setup_method(self):
        # 테스트 공통 데이터
        self.test_request_id = "6123456789abcdef01234567"
        self.test_category = "기술"
    
    def test_update_category_recommendation_result_success(self, client):
        # given
        request_data = {
            "predicted_category": self.test_category
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.update_recommendation_result') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = CategoryRecommendationStatusResponse(
                request_id=self.test_request_id,
                is_completed=True,
                predicted_category=self.test_category
            )
            
            # when
            response = client.post(f"/ai-proxy/category-recommendation-results/{self.test_request_id}", json=request_data)
            
            # then
            assert response.status_code == 200
            assert response.json() == {
                "request_id": self.test_request_id,
                "is_completed": True,
                "predicted_category": self.test_category
            }
            
            # 서비스가 한 번 호출됐는지 확인
            mock_service.assert_called_once()
    
    def test_update_category_recommendation_result_not_found(self, client):
        # given
        request_data = {
            "predicted_category": self.test_category
        }
        
        # 서비스 응답 모의 설정 - 업데이트 실패
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.update_recommendation_result') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = None
            
            # when
            response = client.post(f"/ai-proxy/category-recommendation-results/{self.test_request_id}", json=request_data)
            
            # then
            assert response.status_code == 404
            assert response.json() == {
                "status": 404,
                "message": "요청을 찾을 수 없습니다.",
                "detail": "존재하지 않는 ID입니다."
            }
            
            # 서비스가 한 번 호출됐는지 확인
            mock_service.assert_called_once() 