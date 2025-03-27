import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).parent

load_dotenv()

def get_database_url():
    """Get database URL and fix potential 'postgres://' to 'postgresql://' for SQLAlchemy."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    return database_url or 'sqlite:///sports_store.db'

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development') 