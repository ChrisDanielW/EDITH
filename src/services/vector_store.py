"""
Vector Store Service for EDITH
Manages Pinecone vector database operations for RAG
"""

import logging
from typing import List, Dict, Optional, Tuple
from pinecone import Pinecone, ServerlessSpec
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using Pinecone"""
    
    def __init__(self, api_key: str, environment: str, index_name: str, dimension: int = 384):
        """
        Initialize Pinecone vector store
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the Pinecone index
            dimension: Dimension of the embeddings (default 384 for MiniLM)
        """
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        self.pc = None
        self.index = None
        
        self.initialize_pinecone()
    
    def initialize_pinecone(self):
        """Initialize Pinecone connection and create/connect to index"""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists, create if not
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            raise
    
    def upsert_vectors(
        self,
        vectors: List[List[float]],
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Insert or update vectors in the index
        
        Args:
            vectors: List of embedding vectors
            texts: List of text chunks corresponding to vectors
            metadatas: List of metadata dictionaries for each vector
            ids: List of IDs for vectors (generated if not provided)
            
        Returns:
            Dictionary with upsert results
        """
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            if metadatas is None:
                metadatas = [{} for _ in range(len(vectors))]
            
            # Add text to metadata
            for i, (metadata, text) in enumerate(zip(metadatas, texts)):
                metadata['text'] = text
            
            # Prepare vectors for upsert
            vectors_to_upsert = [
                (id_, vector, metadata)
                for id_, vector, metadata in zip(ids, vectors, metadatas)
            ]
            
            logger.info(f"Preparing to upsert {len(vectors_to_upsert)} vectors")
            logger.info(f"Sample IDs: {ids[:3]}")
            logger.info(f"Sample chunk_ids: {[m.get('chunk_id', 'N/A') for m in metadatas[:3]]}")
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                logger.info(f"Upserting batch of {len(batch)} vectors")
                self.index.upsert(vectors=batch)
            
            logger.info(f"Upserted {len(vectors)} vectors to {self.index_name}")
            
            return {
                'success': True,
                'count': len(vectors),
                'ids': ids
            }
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_vectors(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Query the vector store for similar vectors
        
        Args:
            query_vector: The query embedding vector
            top_k: Number of results to return
            filter_dict: Metadata filters
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matching results with scores and metadata
        """
        try:
            # Query the index
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=include_metadata
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                result = {
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', '') if include_metadata else '',
                    'metadata': match.metadata if include_metadata else {}
                }
                formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} matches for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            return []
    
    def delete_vectors(self, ids: List[str]) -> Dict:
        """
        Delete vectors by IDs
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Dictionary with deletion results
        """
        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors from {self.index_name}")
            return {'success': True, 'count': len(ids)}
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_all(self) -> Dict:
        """
        Delete all vectors from the index
        
        Returns:
            Dictionary with deletion results
        """
        try:
            self.index.delete(delete_all=True)
            logger.info(f"Deleted all vectors from {self.index_name}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error deleting all vectors: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the index
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}
    
    def close(self):
        """Close the Pinecone connection"""
        logger.info("Closing Pinecone connection")
        # Pinecone client doesn't require explicit closing in newer versions