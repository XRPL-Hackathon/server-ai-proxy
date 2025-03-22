from typing import Optional
import uuid
from bson import ObjectId
from fastapi import HTTPException, status

from src.main.ai.data.FileDuplicateCheckRepository import FileDuplicateCheckRepository
from src.main.ai.data.FileDuplicateCheckQueue import FileDuplicateCheckQueue
from src.main.ai.models.FileDuplicateCheck import (
    FileDuplicateCheckRequest,
    FileDuplicateCheckResponse,
    FileDuplicateCheckStatusResponse,
    FileDuplicateCheckEmbeddingsRequest
)


class FileDuplicateCheckService:
    def __init__(self, repository: FileDuplicateCheckRepository, queue: FileDuplicateCheckQueue):
        self.repository = repository
        self.queue = queue

    def create_duplicate_check_request(self, request: FileDuplicateCheckRequest) -> FileDuplicateCheckResponse:
        # 파일이 존재하는지 확인
        file = self.repository.get_file_by_id(request.file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="파일을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            )
        
        # MongoDB에 저장 - ObjectId 자동 생성
        document = self.repository.create_duplicate_check_request(
            file_id=request.file_id,
            user_id=request.user_id
        )
        
        # request_id는 MongoDB의 _id를 문자열로 변환
        request_id = str(document["_id"])
        
        # S3 버킷과 키 정보를 가져옴
        s3_bucket = file.get("s3_url", "").split(".s3.amazonaws.com/")[0].replace("https://", "")
        s3_key = file.get("file_key", "")
        
        # 메시지 발행
        self.queue.send_message(
            request_id=request_id,
            user_id=request.user_id,
            s3_bucket=s3_bucket,
            s3_key=s3_key
        )
        
        return FileDuplicateCheckResponse(request_id=request_id)

    def get_duplicate_check_status(self, file_id: str, user_id: str) -> Optional[FileDuplicateCheckStatusResponse]:
        result = self.repository.get_duplicate_check_by_file_id(file_id, user_id)
        
        if not result:
            return None
            
        return FileDuplicateCheckStatusResponse(
            request_id=str(result["_id"]),
            file_id=result["file_id"],
            is_completed=result["is_completed"],
            is_duplicated=result.get("is_duplicated")
        )

    def update_duplicate_check_result(self, request_id: str, request: FileDuplicateCheckEmbeddingsRequest) -> Optional[FileDuplicateCheckStatusResponse]:
        # 요청이 존재하는지 확인
        check_request = self.repository.get_duplicate_check_by_id(request_id)
        if not check_request:
            return None
        
        # 임베딩을 기반으로 중복 검사 결과 결정 - 간단한 예시
        is_duplicated = False
        if request.embeddings and len(request.embeddings) > 0:
            # 실제로는 여기서 임베딩 벡터 유사도 검사 등을 수행해야 함
            # 일단은 간단하게 임베딩이 비어있지 않으면 중복이 아니라고 처리
            is_duplicated = False
        
        # 결과 업데이트
        updated = self.repository.update_duplicate_check_result(
            request_id=request_id,
            is_duplicated=is_duplicated
        )
        
        if not updated:
            return None
            
        return FileDuplicateCheckStatusResponse(
            request_id=str(updated["_id"]),
            file_id=updated["file_id"],
            is_completed=updated["is_completed"],
            is_duplicated=updated.get("is_duplicated")
        ) 