import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    PROJECT_NAME: str = "ResumeFriendly AI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://resumefriendly_admin:SuperSecurePassword2026@localhost:5432/resumefriendly_db"
    )
    
    # JWT Security
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", 
        "b89e9005f32a514d33a6ea2d5e7ef3a31c5520a45b84c8a24bd6436f54dbf9ee"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # ChromaDB
    CHROMADB_HOST: str = os.getenv("CHROMADB_HOST", "localhost")
    CHROMADB_PORT: int = int(os.getenv("CHROMADB_PORT", "8000"))

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
