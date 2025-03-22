import pytest
import uuid
from unittest.mock import MagicMock, patch
from bson import ObjectId
from datetime import datetime, timezone
from fastapi import HTTPException

from src.main.ai.service.FileDuplicateCheckService import FileDuplicateCheckService
from src.main.ai.models.FileDuplicateCheck import (
    FileDuplicateCheckRequest,
    FileDuplicateCheckResponse,
    FileDuplicateCheckStatusResponse,
    FileDuplicateCheckResultRequest
)


class TestFileDuplicateCheckService:
    def setup_method(self):
        # 목업 리포지토리 및 큐 생성
        self.mock_repository = MagicMock()
        self.mock_queue = MagicMock()
        
        # 테스트 대상 서비스 생성
        self.service = FileDuplicateCheckService(self.mock_repository, self.mock_queue)
        
        # 테스트 공통 데이터
        self.test_file_id = "6123456789abcdef01234567"
        self.test_user_id = "12345678-1234-5678-1234-567812345678"
        self.test_request_id = "7123456789abcdef01234567"
        self.test_object_id = ObjectId(self.test_request_id)
        self.test_file_object_id = ObjectId(self.test_file_id)
        self.test_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    
    def test_create_duplicate_check_request_success(self):
        # given
        request = FileDuplicateCheckRequest(
            user_id=self.test_user_id,
            file_id=self.test_file_id
        )
        
        # 파일 존재함
        file_document = {
            "_id": self.test_file_object_id,
            "s3_bucket": "test-bucket",
            "s3_key": "example.pdf",
            "file_key": "example.pdf",
            "s3_url": "https://bucket.s3.amazonaws.com/example.pdf"
        }
        self.mock_repository.get_file_by_id.return_value = file_document
        
        # 기존 요청 없음
        self.mock_repository.get_duplicate_check_by_file_id.return_value = None
        
        # 요청 생성 응답
        mongo_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.test_time
        }
        self.mock_repository.create_duplicate_check_request.return_value = mongo_document
        
        # when
        result = self.service.create_duplicate_check_request(request)
        
        # then
        self.mock_repository.get_file_by_id.assert_called_once_with(self.test_file_id)
        self.mock_repository.get_duplicate_check_by_file_id.assert_called_once_with(self.test_file_id, self.test_user_id)
        self.mock_repository.create_duplicate_check_request.assert_called_once_with(
            file_id=self.test_file_id,
            user_id=self.test_user_id
        )
        self.mock_queue.send_message.assert_called_once()
        
        assert isinstance(result, FileDuplicateCheckResponse)
        assert result.request_id == str(self.test_object_id)
    
    def test_create_duplicate_check_request_existing_request(self):
        # given
        request = FileDuplicateCheckRequest(
            user_id=self.test_user_id,
            file_id=self.test_file_id
        )
        
        # 파일 존재함
        file_document = {
            "_id": self.test_file_object_id,
            "s3_bucket": "test-bucket",
            "s3_key": "example.pdf",
            "file_key": "example.pdf",
            "s3_url": "https://bucket.s3.amazonaws.com/example.pdf"
        }
        self.mock_repository.get_file_by_id.return_value = file_document
        
        # 이미 요청이 존재함
        existing_check = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.test_time
        }
        self.mock_repository.get_duplicate_check_by_file_id.return_value = existing_check
        
        # when & then
        with pytest.raises(HTTPException) as exc_info:
            self.service.create_duplicate_check_request(request)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "이미 중복 검사 요청이 존재합니다."
        
        self.mock_repository.get_file_by_id.assert_called_once_with(self.test_file_id)
        self.mock_repository.get_duplicate_check_by_file_id.assert_called_once_with(self.test_file_id, self.test_user_id)
        self.mock_repository.create_duplicate_check_request.assert_not_called()
        self.mock_queue.send_message.assert_not_called()
    
    def test_create_duplicate_check_request_file_not_found(self):
        # given
        request = FileDuplicateCheckRequest(
            user_id=self.test_user_id,
            file_id=self.test_file_id
        )
        
        # 파일이 없음
        self.mock_repository.get_file_by_id.return_value = None
        
        # when & then
        with pytest.raises(HTTPException) as exc_info:
            self.service.create_duplicate_check_request(request)
        
        assert exc_info.value.status_code == 404
        self.mock_repository.get_file_by_id.assert_called_once_with(self.test_file_id)
        self.mock_repository.get_duplicate_check_by_file_id.assert_not_called()
        self.mock_repository.create_duplicate_check_request.assert_not_called()
        self.mock_queue.send_message.assert_not_called()
    
    def test_get_duplicate_check_status_exists(self):
        # given
        # 리포지토리 응답 설정 - 완료되지 않은 중복 검사
        mongo_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.test_time
        }
        self.mock_repository.get_duplicate_check_by_file_id.return_value = mongo_document
        
        # when
        result = self.service.get_duplicate_check_status(self.test_file_id, self.test_user_id)
        
        # then
        self.mock_repository.get_duplicate_check_by_file_id.assert_called_once_with(
            self.test_file_id, 
            self.test_user_id
        )
        
        assert isinstance(result, FileDuplicateCheckStatusResponse)
        assert result.request_id == str(self.test_object_id)
        assert result.file_id == self.test_file_id
        assert result.is_completed == False
        assert result.is_duplicated is None
    
    def test_get_duplicate_check_status_completed(self):
        # given
        # 리포지토리 응답 설정 - 완료된 중복 검사
        mongo_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": True,
            "is_duplicated": False,
            "created_at": self.test_time
        }
        self.mock_repository.get_duplicate_check_by_file_id.return_value = mongo_document
        
        # when
        result = self.service.get_duplicate_check_status(self.test_file_id, self.test_user_id)
        
        # then
        self.mock_repository.get_duplicate_check_by_file_id.assert_called_once_with(
            self.test_file_id, 
            self.test_user_id
        )
        
        assert isinstance(result, FileDuplicateCheckStatusResponse)
        assert result.request_id == str(self.test_object_id)
        assert result.file_id == self.test_file_id
        assert result.is_completed == True
        assert result.is_duplicated == False
    
    def test_get_duplicate_check_status_not_found(self):
        # given
        # 리포지토리 응답 설정 - 문서 없음
        self.mock_repository.get_duplicate_check_by_file_id.return_value = None
        
        # when
        result = self.service.get_duplicate_check_status(self.test_file_id, self.test_user_id)
        
        # then
        self.mock_repository.get_duplicate_check_by_file_id.assert_called_once_with(
            self.test_file_id, 
            self.test_user_id
        )
        
        assert result is None
    
    def test_update_duplicate_check_result_success(self):
        # given
        is_duplicated = False
        
        # 요청이 존재함
        check_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": False,
            "is_duplicated": None,
            "created_at": self.test_time
        }
        self.mock_repository.get_duplicate_check_by_id.return_value = check_document
        
        # 파일 중복 상태 업데이트 성공
        self.mock_repository.update_file_duplicate_status.return_value = {
            "_id": self.test_file_object_id,
            "s3_bucket": "test-bucket", 
            "s3_key": "example.pdf",
            "is_duplicated": False
        }
        
        # 업데이트 응답
        updated_document = {
            "_id": self.test_object_id,
            "file_id": self.test_file_id,
            "user_id": self.test_user_id,
            "is_completed": True,
            "is_duplicated": False,
            "created_at": self.test_time,
            "updated_at": datetime(2023, 1, 2, tzinfo=timezone.utc)
        }
        self.mock_repository.update_duplicate_check_result.return_value = updated_document
        
        # when
        result = self.service.update_duplicate_check_result(self.test_request_id, is_duplicated)
        
        # then
        self.mock_repository.get_duplicate_check_by_id.assert_called_once_with(self.test_request_id)
        self.mock_repository.update_file_duplicate_status.assert_called_once_with(self.test_file_id, is_duplicated)
        self.mock_repository.update_duplicate_check_result.assert_called_once_with(
            request_id=self.test_request_id,
            is_duplicated=is_duplicated
        )
        
        assert result == True
    
    def test_update_duplicate_check_result_not_found(self):
        # given
        is_duplicated = False
        
        # 요청이 존재하지 않음
        self.mock_repository.get_duplicate_check_by_id.return_value = None
        
        # when
        result = self.service.update_duplicate_check_result(self.test_request_id, is_duplicated)
        
        # then
        self.mock_repository.get_duplicate_check_by_id.assert_called_once_with(self.test_request_id)
        self.mock_repository.update_file_duplicate_status.assert_not_called()
        self.mock_repository.update_duplicate_check_result.assert_not_called()
        
        assert result == False 