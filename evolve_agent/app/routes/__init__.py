from fastapi import APIRouter

from .n8n import router as n8n_router
from .tests import router as test_router

# Create main router that includes all other routers
router = APIRouter()

# Include sub-routers
router.include_router(test_router, prefix="/tests", tags=["tests"])
router.include_router(n8n_router, prefix="/n8n", tags=["n8n"])
