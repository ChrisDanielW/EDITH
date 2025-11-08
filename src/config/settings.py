"""
EDITH Configuration Settings
Centralized configuration for the EDITH application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """EDITH Configuration Settings"""
    
    # ========== Pinecone Vector Database Settings ==========
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "edith-notes")
    VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", 384))  # For sentence-transformers
    
    # ========== LLaMA Model Settings ==========
    LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "llama-2-7b-chat")
    LLAMA_MODEL_TYPE = os.getenv("LLAMA_MODEL_TYPE", "llama-2-7b-chat.gguf")
    USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2048))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    
    # ========== Embedding Model Settings ==========
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cuda" if USE_GPU else "cpu")
    
    # ========== Document Processing Settings ==========
    NOTES_DIRECTORY = os.getenv("NOTES_DIRECTORY", "./src/data/notes")
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc', '.txt', '.md', '.png', '.jpg', '.jpeg']
    USE_OCR = os.getenv("USE_OCR", "true").lower() == "true"
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))  # Characters per chunk
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # ========== RAG Settings ==========
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))  # Number of relevant chunks to retrieve
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.7))
    
    # ========== Summary Settings ==========
    SUMMARY_MAX_LENGTH = int(os.getenv("SUMMARY_MAX_LENGTH", 500))  # tokens
    SUMMARY_MIN_LENGTH = int(os.getenv("SUMMARY_MIN_LENGTH", 100))  # tokens
    SUMMARY_STYLE = os.getenv("SUMMARY_STYLE", "comprehensive")  # comprehensive, bullet, brief
    
    # ========== Application Settings ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
    MAX_NOTES_TO_PROCESS = int(os.getenv("MAX_NOTES_TO_PROCESS", 100))
    
    # ========== Paths ==========
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "src" / "data"
    MODELS_DIR = BASE_DIR / "models"
    
    @classmethod
    def validate(cls):
        """Validate critical settings"""
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is required")
        
        # Create directories if they don't exist
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        return True


# Create settings instance
settings = Settings()