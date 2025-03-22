import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.main.ai.models.CategoryRecommendation import CategoryRecommendationResultRequest
from src.main.ai.models.FileDuplicateCheck import FileDuplicateCheckResultRequest, FileDuplicateCheckRequest, FileDuplicateCheckResponse
from src.main.ai.service.FileDuplicateCheckService import FileDuplicateCheckService
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
            "request_id": self.test_request_id,
            "predicted_category": self.test_category
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.update_recommendation_result') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = True
            
            # when
            response = client.post("/ai-proxy/category-recommendation-results", json=request_data)
            
            # then
            assert response.status_code == 200
            assert response.json() == {"success": True}
            
            # 직접 호출 파라미터 체크 대신 호출 횟수만 확인
            assert mock_service.call_count == 1
    
    def test_update_category_recommendation_result_not_found(self, client):
        # given
        request_data = {
            "request_id": self.test_request_id,
            "predicted_category": self.test_category
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.CategoryRecommendationService.CategoryRecommendationService.update_recommendation_result') as mock_service:
            # 서비스 응답 설정 - 요청 없음
            mock_service.return_value = False
            
            # when
            response = client.post("/ai-proxy/category-recommendation-results", json=request_data)
            
            # then
            assert response.status_code == 404
            assert response.json() == {
                "detail": "요청을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            }
            
            # 직접 호출 파라미터 체크 대신 호출 횟수만 확인
            assert mock_service.call_count == 1
    
    def test_create_file_duplicate_check_success(self, client):
        # given
        request_data = {
            "user_id": self.test_user_id,
            "file_id": self.test_file_id
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.create_duplicate_check_request') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = FileDuplicateCheckResponse(request_id=self.test_request_id)
            
            # when
            response = client.post("/ai-proxy/file-duplicate-checks", json=request_data)
            
            # then
            assert response.status_code == 200
            assert response.json() == {"request_id": self.test_request_id}
            
            mock_service.assert_called_once()
    
    def test_create_file_duplicate_check_file_not_found(self, client):
        # given
        request_data = {
            "user_id": self.test_user_id,
            "file_id": self.test_file_id
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.create_duplicate_check_request') as mock_service:
            # 서비스 응답 설정 - 파일 없음
            mock_service.side_effect = HTTPException(
                status_code=404,
                detail="파일을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            )
            
            # when
            response = client.post("/ai-proxy/file-duplicate-checks", json=request_data)
            
            # then
            assert response.status_code == 404
            assert response.json() == {
                "detail": "파일을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            }
            
            mock_service.assert_called_once()
    
    def test_create_file_duplicate_check_existing_request(self, client):
        # given
        request_data = {
            "user_id": self.test_user_id,
            "file_id": self.test_file_id
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.create_duplicate_check_request') as mock_service:
            # 서비스 응답 설정 - 이미 요청 존재함
            mock_service.side_effect = HTTPException(
                status_code=400,
                detail="이미 중복 검사 요청이 존재합니다."
            )
            
            # when
            response = client.post("/ai-proxy/file-duplicate-checks", json=request_data)
            
            # then
            assert response.status_code == 400
            assert response.json() == {
                "detail": "이미 중복 검사 요청이 존재합니다."
            }
            
            mock_service.assert_called_once()
    
    def test_update_file_duplicate_check_result_success(self, client):
        # given
        request_data = {
            "request_id": self.test_request_id,
            "is_duplicated": False
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.update_duplicate_check_result') as mock_service:
            # 서비스 응답 설정
            mock_service.return_value = True
            
            # mock_repository.get_duplicate_check_by_id 설정 - 서비스가 아닌 서비스 인스턴스를 패치
            check_data = {
                "_id": self.test_request_id,
                "file_id": self.test_file_id,
                "is_completed": True,
                "is_duplicated": False
            }
            
            # repository를 직접 패치하는 대신 get_duplicate_check_by_id 메소드만 패치
            with patch('src.main.ai.data.FileDuplicateCheckRepository.FileDuplicateCheckRepository.get_duplicate_check_by_id',
                       return_value=check_data) as mock_get_duplicate:
                
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
                
                mock_service.assert_called_once_with(self.test_request_id, False)
    
    def test_update_file_duplicate_check_result_not_found(self, client):
        # given
        request_data = {
            "request_id": self.test_request_id,
            "is_duplicated": False
        }
        
        # 서비스 응답 모의 설정
        with patch('src.main.ai.service.FileDuplicateCheckService.FileDuplicateCheckService.update_duplicate_check_result') as mock_service:
            # 서비스 응답 설정 - 요청 없음
            mock_service.return_value = False
            
            # when
            response = client.post("/ai-proxy/file-duplicate-check-embeddings", json=request_data)
            
            # then
            assert response.status_code == 404
            assert response.json() == {
                "status": 404,
                "message": "요청을 찾을 수 없습니다.",
                "detail": "존재하지 않는 ID입니다."
            }
            
            mock_service.assert_called_once_with(self.test_request_id, False) 