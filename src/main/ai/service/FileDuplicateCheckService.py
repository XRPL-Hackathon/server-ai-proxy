from fastapi import HTTPException, status
from bson import ObjectId
import json

from src.main.ai.models.FileDuplicateCheck import (
    FileDuplicateCheckRequest,
    FileDuplicateCheckResponse,
    FileDuplicateCheckStatusResponse,
    FileDuplicateCheckResultRequest,
    FileDuplicateCheckEmbeddingsRequest
)


class FileDuplicateCheckService:
    def __init__(self, repository, sqs_service):
        self.repository = repository
        self.sqs_service = sqs_service
    
    def create_duplicate_check_request(self, request: FileDuplicateCheckRequest) -> FileDuplicateCheckResponse:
        """
        파일 중복 검사 요청을 생성하고 SQS에 메시지를 발송합니다.
        """
        # 1. 파일 존재 여부 확인
        file = self.repository.get_file_by_id(request.file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="파일을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            )
        
        # 2. 중복 검사 결과가 있는지 확인
        existing_check = self.repository.get_duplicate_check_by_file_id(request.file_id, request.user_id)
        if existing_check:
            return FileDuplicateCheckResponse(request_id=str(existing_check["_id"]))
        
        # 3. 중복 검사 요청 생성
        result = self.repository.create_duplicate_check_request(
            file_id=request.file_id,
            user_id=request.user_id
        )
        
        # 4. SQS에 메시지 발송
        file_data = {
            "s3_bucket": file["s3_bucket"],
            "s3_key": file["s3_key"]
        }
        
        message = {
            "request_type": "file_duplicate_check_embedding_file",
            "request_id": str(result["_id"]),
            "user_id": request.user_id,
            "payload": file_data
        }
        
        self.sqs_service.send_message(json.dumps(message))
        
        # 5. 요청 ID 응답
        return FileDuplicateCheckResponse(request_id=str(result["_id"]))
    
    def get_duplicate_check_status(self, file_id: str, user_id: str) -> FileDuplicateCheckStatusResponse:
        """
        파일 중복 검사 상태를 조회합니다.
        """
        # 1. 중복 검사 요청 조회
        check = self.repository.get_duplicate_check_by_file_id(file_id, user_id)
        
        # 2. 요청이 없으면 None 반환
        if not check:
            return None
        
        # 3. 요청이 있으면 상태 반환
        return FileDuplicateCheckStatusResponse(
            request_id=str(check["_id"]),
            file_id=check["file_id"],
            is_completed=check["is_completed"],
            is_duplicated=check["is_duplicated"]
        )
    
    def update_duplicate_check_result(self, request_id: str, is_duplicated: bool) -> bool:
        """
        파일 중복 검사 결과를 업데이트합니다.
        """
        # 1. 중복 검사 요청 조회
        check = self.repository.get_duplicate_check_by_id(request_id)
        
        # 2. 요청이 없으면 False 반환
        if not check:
            return False
        
        # 3. 파일 중복 상태 업데이트
        file_result = self.repository.update_file_duplicate_status(check["file_id"], is_duplicated)
        
        # 4. 중복 검사 결과 업데이트
        result = self.repository.update_duplicate_check_result(
            request_id=request_id,
            is_duplicated=is_duplicated
        )
        
        # 5. 업데이트 성공 여부 반환
        return result is not None 