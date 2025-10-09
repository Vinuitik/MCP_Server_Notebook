import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Settings:
    def __init__(self):
        # Load YAML configuration
        self.config = self._load_config()
        
        # App settings from config
        app_config = self.config.get("app", {})
        self.app_name = app_config.get("name", "MCP Notebook AI Agent")
        self.app_version = app_config.get("version", "1.0.0")
        self.host = app_config.get("host", "0.0.0.0")
        self.port = app_config.get("port", 8001)
        self.debug = app_config.get("debug", False)
        self.log_level = app_config.get("log_level", "INFO")
        
        # LLM settings from config
        llm_config = self.config.get("llm", {})
        self.llm_model = llm_config.get("model", "gemini-2.0-flash-exp")
        self.llm_temperature = llm_config.get("temperature", 0.7)
        self.llm_max_tokens = llm_config.get("max_tokens", 4096)
        self.llm_timeout = llm_config.get("timeout", 30)
        
        # Google ADC Configuration
        self.google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./service-account-key.json")
        if not os.path.exists(self.google_credentials_path):
            raise ValueError(f"Google service account key file not found at: {self.google_credentials_path}")
        
        # MCP settings from config and environment
        mcp_config = self.config.get("mcp", {})
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", mcp_config.get("server_url", "http://localhost:8002"))
        self.mcp_timeout = mcp_config.get("timeout", 30)
        self.mcp_retry_attempts = mcp_config.get("retry_attempts", 3)
        
        # CORS configuration
        security_config = self.config.get("security", {})
        self.cors_config = security_config.get("cors", {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        })
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            # Apply environment-specific overrides
            env = os.getenv("ENVIRONMENT", "development").lower()
            if env in config:
                self._deep_update(config, config[env])
                
            return config
        except FileNotFoundError:
            print(f"Warning: Configuration file {config_path} not found. Using defaults.")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            return {}
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

settings = Settings()
