from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    DIFY_API_BASE: str = Field(default="http://api:5001")
    DIFY_API_KEY: str = Field(default="your-api-key")
    SUB_DOMAIN: str = Field(default="my-api")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
