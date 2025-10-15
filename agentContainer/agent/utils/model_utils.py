import os
import logging
import traceback
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('AGENT')

_model = None

def get_model():
    """Get or create the ChatGoogleGenerativeAI model with proper credentials"""
    global _model
    if _model is None:
        logger.debug("🤖 Initializing ChatGoogleGenerativeAI model...")
        try:
            # Set up Google ADC credentials
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './service-account-key.json')
            
            if not os.path.exists(credentials_path):
                error_msg = f"Google service account key file not found at: {credentials_path}"
                logger.error(f"❌ CRITICAL: {error_msg}")
                print(f"❌ CRITICAL: {error_msg}")
                raise ValueError(error_msg)
            
            # Set the environment variable for Google ADC
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            logger.debug(f"🔑 Google ADC credentials set: {credentials_path}")
            
            # Get model name from environment or use default
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0')
            logger.debug(f"🎯 Using model: {model_name}")
            
            # Initialize the model
            _model = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.7,  # Add some creativity
                max_tokens=4096   # Higher token limit for Gemini
            )
            logger.info(f"✅ ChatGoogleGenerativeAI model ({model_name}) initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize ChatGoogleGenerativeAI: {e}"
            logger.error(f"❌ CRITICAL: {error_msg}")
            logger.error(f"💥 Model initialization traceback: {traceback.format_exc()}")
            print(f"❌ CRITICAL: {error_msg}")
            raise e
    else:
        logger.debug("🤖 Using cached ChatGoogleGenerativeAI model")
    
    return _model
