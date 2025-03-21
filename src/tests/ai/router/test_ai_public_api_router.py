import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from src.main.ai.models.CategoryRecommendation import (
    CategoryRecommendationRequest,
    CategoryRecommendationResponse,
    CategoryRecommendationStatusResponse
)
from src.main.ai.router.AIPublicAPIRouter import router as public_router
from src.main.auth.dependencies import get_current_user


# 테스트용 앱 생성
app = FastAPI()
app.include_router(public_router)

# 고정된 사용자 ID를 반환하는 의존성 함수
async def mock_get_current_user():
    return uuid.UUID("12345678-1234-5678-1234-567812345678")

# 실제 의존성 대신 모의 의존성 사용
app.dependency_overrides[get_current_user] = mock_get_current_user

# 테스트용 클라이언트
@pytest.fixture
def client():
    return TestClient(app)


class TestAIPublicAPIRouter:
    def setup_method(self):
        # 테스트 공통 데이터
        self.test_title = "테스트 제목"
        self.test_user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        self.test_request_id = "6123456789abcdef01234567"
    
    def test_create_category_recommendation_request(self, client):
        # given
        request_data = {
            "title": self.test_title
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.create_recommendation_request') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = CategoryRecommendationResponse(request_id=self.test_request_id)
            
            # when
            response = client.post("/ai/category-recommendations", json=request_data)
            
            # then
            assert response.status_code == 200
            assert response.json() == {"request_id": self.test_request_id}
            
            # 서비스가 한 번 호출됐는지 확인
            mock_service.assert_called_once()
    
    def test_get_category_recommendation_status_exists(self, client):
        # given
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.get_recommendation_status') as mock_service:
            # 서비스 응답 설정 - 완료된 추천
            mock_service.return_value = CategoryRecommendationStatusResponse(
                request_id=self.test_request_id,
                is_completed=True,
                predicted_category="기술"
            )
            
            # when
            response = client.get(f"/ai/category-recommendations/{self.test_request_id}")
            
            # then
            assert response.status_code == 200
            assert response.json() == {
                "request_id": self.test_request_id,
                "is_completed": True,
                "predicted_category": "기술"
            }
            
            # 서비스가 한 번 호출됐는지 확인
            mock_service.assert_called_once()
    
    def test_get_category_recommendation_status_not_found(self, client):
        # given
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.get_recommendation_status') as mock_service:
            # 서비스 응답 설정 - 요청 없음
            mock_service.return_value = None
            
            # when
            response = client.get(f"/ai/category-recommendations/{self.test_request_id}")
            
            # then
            assert response.status_code == 404
            assert "요청을 찾을 수 없습니다" in response.json().get("detail", "") 