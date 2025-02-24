from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .utils import setup_logger

project_root = Path(__file__).parent.parent

API_PREFIX = "/api/v1"
app = FastAPI(title="Evolve Agent", description="API for managing Evolve Agent")
logger = setup_logger(project_root / "logs" / "app.log")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes under the API prefix
app.include_router(router, prefix=API_PREFIX)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
