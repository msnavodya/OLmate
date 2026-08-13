import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings:
    # App settings
    APP_NAME: str = "OL Mate API"
    APP_VERSION: str = "1.0.0"
    
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://user:password@cluster.mongodb.net/olmate")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "olmate")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    # Debug / security toggles
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")
    ALLOW_INSECURE_FALLBACK: bool = os.getenv("ALLOW_INSECURE_FALLBACK", "False").lower() in ("1", "true", "yes")
    # Logging
    LOG_FILE: str = os.getenv("LOG_FILE", str(PROJECT_ROOT / "backend.log"))
    
    # CORS
    CORS_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,https://olmate.vercel.app",
        ).split(",")
        if origin.strip()
    ]
    
    # ChromaDB
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_data")
    KNOWLEDGE_BASE_PATH: str = os.getenv(
        "KNOWLEDGE_BASE_PATH",
        str(PROJECT_ROOT / "knowledge_base"),
    )

settings = Settings()
