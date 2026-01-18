# app/api/routes/__init__.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from fastapi import APIRouter
from app.api.routes.users import router as users_router
from app.api.routes.journeys import router as journeys_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.dashboard import router as dashboard_router

router = APIRouter(prefix="/api")

router.include_router(users_router)
router.include_router(journeys_router)
router.include_router(alerts_router)
router.include_router(dashboard_router)
