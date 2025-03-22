from fastapi import HTTPException


class FileNotFoundException(HTTPException):
    """
    파일을 찾을 수 없을 때 발생하는 예외
    """
    
    def __init__(self, file_id: str):
        super().__init__(
            status_code=404, 
            detail=f"File with ID '{file_id}' not found"
        ) 