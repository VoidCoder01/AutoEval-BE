import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///autoeval.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'py', 'js', 'java', 'cpp', 'c', 'txt', 'md', 'pdf', 'zip', 'html', 'css', 'json', 'yml', 'yaml'}
    EVALUATION_MODEL = 'unixcoder'  # Using UniXCoder by default
    USE_CODELLAMA = False  # Set to True for CodeLlama explanations (requires more RAM)

