import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient

from src.main.ai.models.CategoryRecommendation import (
    CategoryRecommendationRequest,
    CategoryRecommendationResponse,
    CategoryRecommendationStatusResponse
)
from src.main.ai.models.FileDuplicateCheck import FileDuplicateCheckStatusResponse
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
        self.test_file_id = "67dd86ac60a0a6d929904d47"
        self.test_user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        self.test_request_id = "6123456789abcdef01234567"
        self.test_check_file_id = "7123456789abcdef01234567"
    
    def test_create_category_recommendation_request(self, client):
        # given
        request_data = {
            "file_id": self.test_file_id
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.create_recommendation_request') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = CategoryRecommendationResponse(request_id=self.test_request_id)
            
            # when
            response = client.post("/ai/category-recommendations", json=request_data)
            
            # then
            assert response.status_code == 200
            assert response.json() == {
                "request_id": self.test_request_id
            }
            mock_service.assert_called_once()
    
    def test_get_category_recommendation_status_exists(self, client):
        # given
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.get_recommendation_status') as mock_service:
            # 서비스 응답 설정
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
            mock_service.assert_called_once()
    
    def test_get_category_recommendation_status_not_found(self, client):
        # given
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.get_recommendation_status') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = None
            
            # when
            response = client.get(f"/ai/category-recommendations/{self.test_request_id}")
            
            # then
            assert response.status_code == 404
            assert response.json() == {
                "detail": "요청을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            }
            mock_service.assert_called_once()
    
    def test_get_file_duplicate_check_status_exists(self, client):
        # given
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.get_duplicate_check_status') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = FileDuplicateCheckStatusResponse(
                request_id=self.test_request_id,
                file_id=self.test_check_file_id,
                is_completed=True,
                is_duplicated=False
            )
            
            # when
            response = client.get(f"/ai/file-duplicate-checks?file_id={self.test_check_file_id}")
            
            # then
            assert response.status_code == 200
            assert response.json() == {
                "request_id": self.test_request_id,
                "file_id": self.test_check_file_id,
                "is_completed": True,
                "is_duplicated": False
            }
            mock_service.assert_called_once_with(self.test_check_file_id, str(self.test_user_id))
    
    def test_get_file_duplicate_check_status_not_found(self, client):
        # given
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.get_duplicate_check_status') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = None
            
            # when
            response = client.get(f"/ai/file-duplicate-checks?file_id={self.test_check_file_id}")
            
            # then
            assert response.status_code == 404
            assert response.json() == {
                "detail": "요청을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            }
            mock_service.assert_called_once_with(self.test_check_file_id, str(self.test_user_id)) 