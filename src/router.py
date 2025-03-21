from fastapi import APIRouter

from src.main.health.router import HealthAPIRouter
from src.main.ai.router.AIPublicAPIRouter import router as ai_public_router
from src.main.ai.router.AIInternalAPIRouter import router as ai_internal_router


router = APIRouter(
    prefix="",
)

router.include_router(HealthAPIRouter.router)
router.include_router(ai_public_router)
router.include_router(ai_internal_router)