"""
EDITH - Even Disconnected, I'm The Helper
Main application entry point for the RAG-based notes assistant
"""

import os
import sys
import logging
from pathlib import Path
from tqdm import tqdm

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from models.llama_client import LlamaClient
from services.vector_store import VectorStore
from services.rag_service import RAGService
from utils.embeddings import EmbeddingGenerator
from utils.document_loader import DocumentLoader
from utils.text_chunker import SmartChunker

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EDITH:
    """Main EDITH application class"""
    
    def __init__(self):
        """Initialize EDITH components"""
        logger.info("=" * 60)
        logger.info("Initializing EDITH - Even Disconnected, I'm The Helper")
        logger.info("=" * 60)
        
        # Validate settings
        settings.validate()
        
        # Initialize components
        self.embedding_generator = None
        self.vector_store = None
        self.llama_client = None
        self.rag_service = None
        self.document_loader = None
        self.text_chunker = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all EDITH components"""
        try:
            # 1. Initialize embedding generator
            logger.info("Loading embedding model...")
            self.embedding_generator = EmbeddingGenerator(
                model_name=settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE
            )
            
            # 2. Initialize vector store
            logger.info("Connecting to Pinecone vector store...")
            self.vector_store = VectorStore(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT,
                index_name=settings.PINECONE_INDEX_NAME,
                dimension=self.embedding_generator.get_embedding_dimension()
            )
            
            # 3. Initialize LLaMA client
            logger.info("Loading LLaMA model (this may take a while)...")
            self.llama_client = LlamaClient(
                model_path=settings.LLAMA_MODEL_PATH,
                model_type="gguf",  # or "transformers"
                use_gpu=settings.USE_GPU,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            
            # 4. Initialize RAG service
            logger.info("Setting up RAG service...")
            self.rag_service = RAGService(
                vector_store=self.vector_store,
                llama_client=self.llama_client,
                embedding_generator=self.embedding_generator,
                top_k=settings.TOP_K_RESULTS,
                similarity_threshold=settings.SIMILARITY_THRESHOLD
            )
            
            # 5. Initialize document loader and text chunker
            self.document_loader = DocumentLoader(use_ocr=settings.USE_OCR)
            self.text_chunker = SmartChunker(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            
            logger.info("✓ All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            raise
    
    def ingest_documents(self, directory: str = None, recursive: bool = True):
        """
        Ingest documents from a directory into the vector store
        
        Args:
            directory: Path to documents directory (defaults to settings.NOTES_DIRECTORY)
            recursive: Whether to search subdirectories
        """
        directory = directory or settings.NOTES_DIRECTORY
        logger.info(f"Ingesting documents from: {directory}")
        
        try:
            # 1. Load documents
            logger.info("Loading documents...")
            documents = self.document_loader.load_directory(directory, recursive=recursive)
            
            if not documents:
                logger.warning("No documents found to ingest")
                return
            
            logger.info(f"Loaded {len(documents)} documents")
            
            # 2. Chunk documents
            logger.info("Chunking documents...")
            chunks = self.text_chunker.chunk_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")
            
            # 3. Generate embeddings
            logger.info("Generating embeddings...")
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_generator.batch_generate_embeddings(
                texts,
                batch_size=settings.BATCH_SIZE,
                show_progress=True
            )
            
            # 4. Prepare metadata
            metadatas = []
            for chunk in chunks:
                metadata = chunk.get('metadata', {}).copy()  # Important: copy to avoid reference issues
                metadata['chunk_id'] = chunk.get('chunk_id', 0)
                metadata['char_count'] = chunk.get('char_count', 0)
                metadatas.append(metadata)
            
            # 5. Upsert to vector store
            logger.info("Upserting to vector store...")
            result = self.vector_store.upsert_vectors(
                vectors=embeddings,
                texts=texts,
                metadatas=metadatas
            )
            
            if result['success']:
                logger.info(f"✓ Successfully ingested {result['count']} chunks")
                
                # Show index stats
                stats = self.vector_store.get_index_stats()
                logger.info(f"Index stats: {stats}")
            else:
                logger.error(f"Error ingesting documents: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"Error during document ingestion: {str(e)}")
            raise
    
    def query(self, question: str, filter_metadata: dict = None) -> dict:
        """
        Query the knowledge base
        
        Args:
            question: User's question
            filter_metadata: Optional metadata filters
            
        Returns:
            Dictionary with answer and sources
        """
        logger.info(f"Query: {question}")
        result = self.rag_service.query(question, filter_metadata)
        
        logger.info(f"Answer confidence: {result['confidence']:.2f}")
        logger.info(f"Used {result['num_sources']} sources")
        
        return result
    
    def summarize(self, filter_metadata: dict = None, style: str = "comprehensive") -> str:
        """
        Generate a summary of notes
        
        Args:
            filter_metadata: Optional metadata filters
            style: Summary style (comprehensive, bullet, brief)
            
        Returns:
            Summary text
        """
        logger.info(f"Generating {style} summary...")
        summary = self.rag_service.summarize_notes(filter_metadata, style)
        return summary
    
    def interactive_mode(self):
        """Run EDITH in interactive chat mode"""
        logger.info("\n" + "=" * 60)
        logger.info("EDITH Interactive Mode")
        logger.info("Commands: 'quit' to exit, 'summary' for note summary")
        logger.info("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("Goodbye!")
                    break
                
                if user_input.lower() == 'summary':
                    print("\nEDITH: Generating summary...")
                    summary = self.summarize(style="comprehensive")
                    print(f"\nEDITH: {summary}\n")
                    continue
                
                # Regular query
                result = self.query(user_input)
                
                print(f"\nEDITH: {result['answer']}")
                
                if result['sources']:
                    print(f"\nSources ({len(result['sources'])}):")
                    for source in result['sources']:
                        print(f"  - {source['filename']} (relevance: {source['relevance_score']:.2f})")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                print(f"\nEDITH: Sorry, I encountered an error: {str(e)}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EDITH - Your Personal Notes Assistant")
    parser.add_argument('--ingest', action='store_true', help='Ingest documents from notes directory')
    parser.add_argument('--query', type=str, help='Query the knowledge base')
    parser.add_argument('--summary', action='store_true', help='Generate a summary of notes')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--notes-dir', type=str, help='Path to notes directory (for ingestion)')
    
    args = parser.parse_args()
    
    try:
        # Initialize EDITH
        edith = EDITH()
        
        # Handle commands
        if args.ingest:
            edith.ingest_documents(directory=args.notes_dir)
        
        elif args.query:
            result = edith.query(args.query)
            print(f"\n{result['answer']}\n")
            
            if result['sources']:
                print(f"Sources:")
                for source in result['sources']:
                    print(f"  - {source['filename']}")
        
        elif args.summary:
            summary = edith.summarize()
            print(f"\n{summary}\n")
        
        elif args.interactive:
            edith.interactive_mode()
        
        else:
            # Default: interactive mode
            edith.interactive_mode()
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()