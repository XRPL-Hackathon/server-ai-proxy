from pydantic import BaseModel, Field
from typing import Optional, List, Any


class FileDuplicateCheckRequest(BaseModel):
    user_id: str
    file_id: str


class FileDuplicateCheckResponse(BaseModel):
    request_id: str


class FileDuplicateCheckStatusResponse(BaseModel):
    request_id: str
    file_id: str
    is_completed: bool
    is_duplicated: Optional[bool] = None


class FileDuplicateCheckEmbeddingsRequest(BaseModel):
    request_id: str
    embeddings: List[Any] 