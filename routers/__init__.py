from fastapi import APIRouter

from routers import auth, user, articles, simulations

router = APIRouter(prefix="/api")

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(articles.router, prefix="/articles", tags=["articles"])
router.include_router(simulations.router, prefix="/simulations", tags=["simulations"])

__all__ = ["router"]
