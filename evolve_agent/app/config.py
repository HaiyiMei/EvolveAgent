from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # n8n settings
    N8N_BASE_URL: str = Field(default="http://n8n:5678")
    N8N_API_KEY: str = Field(default="your-n8n-api-key")
    OPENAI_API_KEY: str = Field(default="your-openai-api-key")
    OLLAMA_BASE_URL: str = Field(default="http://192.168.2.57:11434")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
