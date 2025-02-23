from traceback import format_exc

import httpx
from fastapi import HTTPException
from loguru import logger

from .config import settings


async def make_dify_request(method: str, endpoint: str, **kwargs):
    """Helper function for making requests to the Dify API."""
    async with httpx.AsyncClient() as client:
        # Set default headers
        headers = {"Authorization": f"Bearer {settings.DIFY_API_KEY}"}

        # Add Content-Type header only for JSON requests
        if "files" not in kwargs:
            headers["Content-Type"] = "application/json"

        # Remove any leading slash to prevent double slashes
        endpoint = endpoint.lstrip("/")

        # Construct the full URL
        url = f"{settings.DIFY_API_BASE}/{endpoint}"

        logger.debug("Making request to Dify API:")
        logger.debug(f"Method: {method}")
        logger.debug(f"URL: {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Args: {kwargs}")

        try:
            response = await client.request(method, url, headers=headers, **kwargs)
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response text: {response.text}")

            if response.status_code >= 400:
                logger.error(f"API error: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
        except httpx.RequestError as e:
            error_msg = format_exc()
            logger.exception(f"Request error: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to connect to Dify API: {error_msg}")
        except Exception as e:
            error_msg = format_exc()
            logger.exception(f"Unexpected error: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {error_msg}")
