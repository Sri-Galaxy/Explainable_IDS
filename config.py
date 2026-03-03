import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload settings...
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 5 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'csv'}
    MAX_ROWS = int(os.getenv('MAX_ROWS', 100))
    
    # Model settings...
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/xgb_model.pkl')
    
    # AI settings...
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    GEMINI_TIMEOUT = int(os.getenv('GEMINI_TIMEOUT', 10))
    
    # SHAP settings...
    SHAP_TIMEOUT = int(os.getenv('SHAP_TIMEOUT', 30))
    
    # Logging...
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')