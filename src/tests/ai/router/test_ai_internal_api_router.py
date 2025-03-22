import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.main.ai.models.CategoryRecommendation import CategoryRecommendationStatusResponse
from src.main.ai.models.FileDuplicateCheck import FileDuplicateCheckStatusResponse
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
        self.test_user_id = "12345678-1234-5678-1234-567812345678"
        self.test_file_id = "7123456789abcdef01234567"
    
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
            
            mock_service.assert_called_once()
    
    def test_update_category_recommendation_result_not_found(self, client):
        # given
        request_data = {
            "predicted_category": self.test_category
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.update_recommendation_result') as mock_service:
            # 서비스 응답 설정 - 요청 없음
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
            
            mock_service.assert_called_once()
    
    def test_update_file_duplicate_check_embeddings_success(self, client):
        # given
        request_data = {
            "request_id": self.test_request_id,
            "embeddings": [1.0, 2.0, 3.0]
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.update_duplicate_check_result') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = FileDuplicateCheckStatusResponse(
                request_id=self.test_request_id,
                file_id=self.test_file_id,
                is_completed=True,
                is_duplicated=False
            )
            
            # when
            response = client.post("/ai-proxy/file-duplicate-check-embeddings", json=request_data)
            
            # then
            assert response.status_code == 200
            assert response.json() == {
                "request_id": self.test_request_id,
                "file_id": self.test_file_id,
                "is_completed": True,
                "is_duplicated": False
            }
            
            mock_service.assert_called_once()
    
    def test_update_file_duplicate_check_embeddings_not_found(self, client):
        # given
        request_data = {
            "request_id": self.test_request_id,
            "embeddings": [1.0, 2.0, 3.0]
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.update_duplicate_check_result') as mock_service:
            # 서비스 응답 설정 - 요청 없음
            mock_service.return_value = None
            
            # when
            response = client.post("/ai-proxy/file-duplicate-check-embeddings", json=request_data)
            
            # then
            assert response.status_code == 404
            assert response.json() == {
                "status": 404,
                "message": "요청을 찾을 수 없습니다.",
                "detail": "존재하지 않는 ID입니다."
            }
            
            mock_service.assert_called_once() 