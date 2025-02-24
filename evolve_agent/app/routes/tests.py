from fastapi import APIRouter, File, UploadFile

from ..config import settings

router = APIRouter()


@router.get("/hello")
async def test():
    """Simple test endpoint."""
    return {"message": "Hello, World!"}


@router.post("/upload")
async def test_upload(file: UploadFile = File(...)):
    """Test file upload endpoint."""
    content = await file.read()
    return {"message": "Hello, World!", "content": content.decode()}


@router.get("/config")
async def test_config():
    """Test configuration endpoint."""
    return {
        "api_base": settings.DIFY_API_BASE,
        "api_key": settings.DIFY_API_KEY[:5] + "..." if settings.DIFY_API_KEY else None,
        "sub_domain": settings.SUB_DOMAIN,
    }
