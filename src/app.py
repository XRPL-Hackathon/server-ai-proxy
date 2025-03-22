from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

from src.router import router


load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

origins = [
    "https://d6jo3bhmz1u5k.cloudfront.net",
    "https://localhost:5173",
    "http://localhost:5173",
]


app = FastAPI(  
    title="xrpedia-ai-proxy",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": 400,
            "message": "잘못된 요청입니다.",
            "detail": "명세에 맞지 않은 요청입니다."
        }
    )


app.include_router(router)