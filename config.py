import os
import sys

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # File Processing Settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB default
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}
    
    # Analysis Settings
    DEFAULT_QUESTION_COUNT = int(os.getenv('DEFAULT_QUESTION_COUNT', '5'))
    SUMMARY_LENGTH = int(os.getenv('SUMMARY_LENGTH', '3'))  # sentences

    @classmethod
    def load_from_file(cls, filepath='.env'):
        """
        Optional: Manual .env file loading without dotenv dependency
        """
        try:
            if os.path.exists(filepath):
                print(f"Loading environment from {filepath}")
                with open(filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
                return True
            return False
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
            return False

    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        warnings = []
        
        if not cls.OPENAI_API_KEY:
            warnings.append("OPENAI_API_KEY not found. Some AI features may not work.")
        
        if cls.MAX_TOKENS <= 0:
            warnings.append("MAX_TOKENS must be positive")
        
        if not (0 <= cls.TEMPERATURE <= 1):
            warnings.append("TEMPERATURE must be between 0 and 1")
        
        if warnings:
            print("Configuration warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return len(warnings) == 0

    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        print("Current Configuration:")
        print(f"  MODEL_NAME: {cls.MODEL_NAME}")
        print(f"  MAX_TOKENS: {cls.MAX_TOKENS}")
        print(f"  TEMPERATURE: {cls.TEMPERATURE}")
        print(f"  DEBUG: {cls.DEBUG}")
        print(f"  LOG_LEVEL: {cls.LOG_LEVEL}")
        print(f"  MAX_FILE_SIZE: {cls.MAX_FILE_SIZE}")
        print(f"  ALLOWED_EXTENSIONS: {cls.ALLOWED_EXTENSIONS}")
        print(f"  OPENAI_API_KEY: {'Set' if cls.OPENAI_API_KEY else 'Not Set'}")

# Try to load from .env file manually (optional)
Config.load_from_file()

# Validate configuration
Config.validate_config()

# Print config in debug mode
if Config.DEBUG:
    Config.print_config()