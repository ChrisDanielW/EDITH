"""
Embedding Generation for EDITH
Handles text embedding generation using sentence transformers
"""

import logging
from typing import List, Union
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using sentence transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cpu"):
        """
        Initialize the embedding generator
        
        Args:
            model_name: Name of the sentence transformer model
            device: Device to run the model on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        logger.info(f"Embedding model loaded on {device}")
    
    def generate_embeddings(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text(s)
        
        Args:
            text: Single text string or list of text strings
            
        Returns:
            Embedding vector(s)
        """
        try:
            # Ensure text is not empty
            if isinstance(text, str):
                if not text.strip():
                    logger.warning("Empty text provided for embedding")
                    return [0.0] * self.model.get_sentence_embedding_dimension()
            elif isinstance(text, list):
                text = [t if t.strip() else " " for t in text]  # Replace empty with space
            
            # Generate embeddings
            embeddings = self.model.encode(
                text,
                convert_to_tensor=False,
                show_progress_bar=False,
                normalize_embeddings=True  # Normalize for cosine similarity
            )
            
            # Convert to list format
            if isinstance(text, str):
                return embeddings.tolist()
            else:
                return embeddings.tolist()
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def batch_generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
        """
        try:
            # Filter out empty texts
            valid_texts = [t if t.strip() else " " for t in texts]
            
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_tensor=False,
                show_progress_bar=show_progress,
                normalize_embeddings=True
            )
            
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error in batch embedding generation: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.model.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0 to 1)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        return float(similarity)


# Convenience functions for backward compatibility
def generate_embeddings(text: Union[str, List[str]], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> Union[List[float], List[List[float]]]:
    """
    Generate embeddings for text(s)
    
    Args:
        text: Single text string or list of text strings
        model_name: Name of the sentence transformer model
        
    Returns:
        Embedding vector(s)
    """
    generator = EmbeddingGenerator(model_name=model_name)
    return generator.generate_embeddings(text)


def batch_generate_embeddings(texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Generate embeddings for a batch of texts
    
    Args:
        texts: List of text strings
        model_name: Name of the sentence transformer model
        
    Returns:
        List of embedding vectors
    """
    generator = EmbeddingGenerator(model_name=model_name)
    return generator.batch_generate_embeddings(texts)