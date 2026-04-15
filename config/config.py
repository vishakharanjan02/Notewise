# Enhanced configuration for Vishakha_Notewise with OpenRouter

import os
from dotenv import load_dotenv

# Load environment variables - override=True ensures .env values win over shell exports
load_dotenv(override=True)

class SimpleConfig:
    """Enhanced configuration class for Vishakha_Notewise with OpenRouter support."""
    
    def __init__(self):
        self.app_name = "Vishakha_Notewise"
        self.debug = os.getenv("DEBUG", "True").lower() == "true"
        
        # OpenRouter API Configuration
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        # Use env variable if it exists, otherwise use a free model as fallback
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-air:free")
        self.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # AI Features
        self.auto_summarize = os.getenv("AUTO_SUMMARIZE", "True").lower() == "true"
        self.auto_generate_title = os.getenv("AUTO_GENERATE_TITLE", "True").lower() == "true"
    
    def get_secret_key(self):
        """Get secret key."""
        return os.getenv("SECRET_KEY", "simple-secret-key-for-vishakha")
    
    def validate_openrouter_config(self):
        """Validate OpenRouter configuration."""
        if not self.openrouter_api_key:
            return False, "OPENROUTER_API_KEY is required. Please set it in your .env file."
        return True, "OpenRouter configuration is valid."
    
    def is_ai_enabled(self):
        """Check if AI features are enabled."""
        return bool(self.openrouter_api_key)

# Global config instance
config = SimpleConfig()
