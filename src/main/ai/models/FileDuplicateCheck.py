from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FileDuplicateCheckRequest(BaseModel):
    """파일 중복 검사 요청 모델"""
    user_id: str
    file_id: str


class FileDuplicateCheckResponse(BaseModel):
    """파일 중복 검사 응답 모델"""
    request_id: str


class FileDuplicateCheckStatusResponse(BaseModel):
    """파일 중복 검사 상태 응답 모델"""
    request_id: str
    file_id: str
    is_completed: bool
    is_duplicated: Optional[bool] = None


class FileDuplicateCheckResultRequest(BaseModel):
    """파일 중복 검사 결과 요청 모델"""
    request_id: str
    is_duplicated: bool


class FileDuplicateCheckEmbeddingsRequest(BaseModel):
    """파일 임베딩 저장 요청 모델"""
    file_id: str
    embeddings: List[float] 