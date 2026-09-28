import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'campusflow-dev-secret')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRY_MINUTES = int(os.getenv('JWT_EXPIRY_MINUTES', '60'))
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    # gemini-2.0-flash has been retired; use a current stable model.
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')
