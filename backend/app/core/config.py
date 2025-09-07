from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus
from typing import List

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

# Load .env
project_path: Path = Path(__file__).parent.parent.parent
env_file_path = project_path / ".env"
load_dotenv(env_file_path)


class Settings(BaseSettings):
    PROJECT_NAME: str = "RoleFit"
    DESCRIPTION: str = "RoleFit Backend API"
    VERSION: str = "0.1.0"
    ENV: str = "development"
    DEBUG: bool = True

    ALLOWED_ORIGINS: List[str] = ["*"]

    LOG_LEVEL: str = "INFO"

    # MongoDB
    MONGO_USER: Optional[str] = None
    MONGO_PASSWORD: Optional[str] = None
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "rolefit_db"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 60
    JWT_SECRET: str = None
    JWT_ALGORITHM: str = "HS256"

    TOKEN_URL: str = "/api/login"

    UPLOAD_DIR: Path = Path("/tmp/resume_uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024

    DEFAULT_WORKSPACE_NAME: str = PROJECT_NAME

    @field_validator("MONGO_PASSWORD", mode="before")
    def encode_password(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return quote_plus(v)
        return v

    @property
    def mongo_uri(self) -> str:
        """Build full MongoDB connection string."""
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return (
                f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}"
                f"@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
            )
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"


settings = Settings()
