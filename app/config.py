import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Security & App Settings
SECRET_KEY = os.getenv("SECRET_KEY", "pocketsmart_super_secure_jwt_secret_key_2026_!@#")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Database
DB_PATH = BASE_DIR / "pocketsmart.db"

# Uploads directory for outfit images and moodboards
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Gemini AI Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Default Currency
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "$")
