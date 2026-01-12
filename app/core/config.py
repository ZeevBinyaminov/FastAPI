import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")
        self.postgres_user = os.getenv("PG_USER", "postgres")
        self.postgres_password = os.getenv("PG_PASSWORD", "postgres")
        self.postgres_host = os.getenv("PG_HOST", "localhost")
        self.postgres_port = os.getenv("PG_PORT", "5432")
        self.postgres_db = os.getenv("PG_DB", "postgres")
        self.postgres_ssl = os.getenv("PG_SSL", "disable")

        if not self.database_url:
            ssl_query = f"?ssl={self.postgres_ssl}" if self.postgres_ssl else ""
            self.database_url = (
                "postgresql+asyncpg://"
                f"{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
                f"{ssl_query}"
            )

        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change_me")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expires_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
        self.admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin")


settings = Settings()
