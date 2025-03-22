from fastapi import HTTPException


class BadRequestException(HTTPException):
    """
    요청이 잘못되었을 때 발생하는 예외
    """
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=400, 
            detail=detail
        ) 