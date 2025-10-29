import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///evalai_new.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024  # 5GB max file size
    ALLOWED_EXTENSIONS = {
        # Core programming languages
        'py', 'js', 'ts', 'jsx', 'tsx', 'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'php', 'rb', 'go', 'rs', 'swift', 'kt', 'scala', 'r', 'matlab', 'm',
        
        # Web technologies
        'html', 'htm', 'css', 'scss', 'sass', 'less', 'vue', 'svelte', 'jsx', 'tsx',
        
        # Configuration and data
        'json', 'xml', 'yml', 'yaml', 'toml', 'ini', 'cfg', 'conf', 'env', 'properties',
        
        # Documentation
        'md', 'txt', 'rst', 'adoc', 'tex',
        
        # Scripts and automation
        'sh', 'bash', 'zsh', 'fish', 'ps1', 'bat', 'cmd',
        
        # Database and queries
        'sql', 'sqlite', 'db',
        
        # Mobile development
        'dart', 'flutter', 'xaml',
        
        # Data science and ML
        'ipynb', 'rmd', 'py', 'r',
        
        # Build and deployment
        'dockerfile', 'docker-compose', 'makefile', 'cmake', 'gradle', 'maven',
        
        # Archives
        'zip', 'tar', 'gz',
        
        # Office documents (for documentation)
        'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'
    }
    
    # RAG Configuration
    # EVALUATION_MODEL = 'opensource'  # 'opensource' (Llama-3-8B) or 'openai' (GPT-4) ⭐ USING OPENAI
    EVALUATION_MODEL = 'openai'  # 'opensource' (Llama-3-8B) or 'openai' (GPT-4) ⭐ USING OPENAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # Set in environment or .env file
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # Can use 'microsoft/unixcoder-base' for code-specific
    CHUNK_SIZE = 512  # Token size for chunks
    CHUNK_OVERLAP = 128  # Overlap between chunks
    RETRIEVAL_TOP_K = 8  # Number of chunks to retrieve
    MAX_CONTEXT_TOKENS = 2000  # Max tokens to send to LLM
    
    # LLM Configuration
    LLM_MODEL = 'meta-llama/Meta-Llama-3-8B-Instruct'  # Main evaluation model
    LLM_TEMPERATURE = 0.3  # Lower = more deterministic
    LLM_MAX_TOKENS = 512  # Max tokens in response
    USE_QUANTIZATION = True  # Use 4-bit quantization (faster & uses ~4GB VRAM instead of 16GB)


