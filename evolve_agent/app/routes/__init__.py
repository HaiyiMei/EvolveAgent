from fastapi import APIRouter

from .tests import router as test_router
from .workflows import router as workflow_router

# Create main router that includes all other routers
router = APIRouter()

# Include sub-routers
router.include_router(workflow_router, prefix="/workflows", tags=["workflows"])
router.include_router(test_router, prefix="/tests", tags=["tests"])
