from fastapi import APIRouter

from .views import router as auth_router


router = APIRouter(tags=["Auth service"])
router.include_router(auth_router)
