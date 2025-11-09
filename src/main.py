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
from utils.query_classifier import QueryClassifier

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
        self.query_classifier = None
        
        # System prompts
        self.rag_system_prompt = """You are EDITH, a precise and helpful AI assistant.
When answering from provided context:
- Be direct and concise (2-3 sentences max unless asked for details)
- Use bullet points for lists
- If uncertain, say so briefly
- Don't add information not in the context"""
        
        self.conversational_system_prompt = """You are EDITH (Even Disconnected, I'm The Helper), a witty and personable AI assistant.

Your personality:
- Friendly and conversational, like talking to a smart colleague
- Occasionally playful or use light humor when appropriate
- Warm and approachable, never stiff or robotic
- Self-aware that you're an AI assistant helping with notes

Response style:
- Keep it natural and brief (1-2 sentences usually)
- Match the user's energy (casual with casual, serious with serious)
- Use contractions (I'm, you're, don't) to sound natural
- Be helpful without being overly formal
- When someone greets you or chats casually, respond naturally without always mentioning notes

Remember: You're helpful, but also have personality. Be real, not corporate."""
        
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
            
            # 6. Initialize query classifier
            logger.info("Setting up query classifier...")
            self.query_classifier = QueryClassifier()
            
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
    
    def query(self, question: str, filter_metadata: dict = None, use_rag: bool = None) -> dict:
        """
        Query with intelligent routing between RAG and conversation
        
        Args:
            question: User's question
            filter_metadata: Optional metadata filters
            use_rag: Force RAG usage (None = auto-detect)
            
        Returns:
            Dictionary with answer and sources
        """
        logger.info(f"Query: {question}")
        
        try:
            # Classify query if not forced
            if use_rag is None:
                classification = self.query_classifier.classify(question)
                use_rag = classification['type'] in ['knowledge', 'hybrid']
                
                logger.info(f"Query classified as: {classification['type']} "
                          f"(confidence: {classification['confidence']:.2f})")
            
            if use_rag:
                # Use RAG for knowledge queries
                return self._query_with_rag(question, filter_metadata)
            else:
                # Use direct conversation for casual queries
                return self._query_conversational(question)
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'answer': "I encountered an error processing your query.",
                'error': str(e),
                'confidence': 0.0,
                'sources': [],
                'num_sources': 0,
                'mode': 'error'
            }
    
    def _query_with_rag(self, question: str, filter_metadata: dict = None) -> dict:
        """Query using RAG (knowledge from notes)"""
        result = self.rag_service.query(question, filter_metadata)
        
        logger.info(f"Answer confidence: {result['confidence']:.2f}")
        logger.info(f"Used {result['num_sources']} sources")
        
        # If no relevant info found in notes, fall back to conversational mode
        if result['num_sources'] == 0 and result['confidence'] == 0.0:
            logger.info("No relevant info in notes, falling back to conversational mode")
            
            # Use LLM to answer conversationally with a subtle hint
            answer = self.llama_client.chat(
                message=question,
                context="",
                system_prompt="""You are EDITH, a helpful AI assistant.

The user asked about something, but you don't have specific information about it in their notes.

Instructions:
- Answer the question naturally based on your general knowledge
- Subtly mention you don't have it in their notes (e.g., "I don't see that in your notes, but..." or "Not in your notes, though..." or "Your notes don't mention this, but...")
- Keep it brief and conversational (2-3 sentences)
- Be helpful despite not having the specific info""",
                max_tokens=200  # Limited tokens for fallback responses
            )
            
            return {
                'answer': answer,
                'confidence': 0.3,  # Lower confidence since it's not from notes
                'sources': [],
                'num_sources': 0,
                'mode': 'conversational-fallback'
            }
        
        result['mode'] = 'rag'
        return result
    
    def _query_conversational(self, question: str) -> dict:
        """Handle conversational queries without RAG"""
        try:
            # Fallback responses for common phrases
            fallback_responses = {
                'hi': "Hey! What's up?",
                'hello': "Hello! How can I help you today?",
                'hey': "Hey there! Need something?",
                'thanks': "You're welcome! 😊",
                'thank you': "Happy to help!",
                'bye': "See ya! Come back anytime.",
                'goodbye': "Catch you later!",
                'how are you': "I'm doing great! Always ready to help with your notes. How about you?",
                'good morning': "Good morning! Ready to tackle the day?",
                'good night': "Good night! Sleep well!",
            }
            
            question_lower = question.lower().strip()
            for key, response in fallback_responses.items():
                if key in question_lower:
                    logger.info("Generated conversational response (fallback)")
                    return {
                        'answer': response,
                        'confidence': 1.0,
                        'sources': [],
                        'num_sources': 0,
                        'mode': 'conversational'
                    }
            
            # Use LLM for other conversational queries (with limited tokens for speed)
            prompt = f"""{self.conversational_system_prompt}

User: {question}

EDITH:"""
            
            answer = self.llama_client.chat(
                message=question,
                context="",
                system_prompt=self.conversational_system_prompt,
                max_tokens=150  # Shorter responses for conversational mode
            )
            
            logger.info("Generated conversational response (LLM)")
            
            return {
                'answer': answer.strip(),
                'confidence': 0.9,
                'sources': [],
                'num_sources': 0,
                'mode': 'conversational'
            }
            
        except Exception as e:
            logger.error(f"Error in conversational query: {str(e)}")
            return {
                'answer': "I'm here to help! Ask me about your notes or just chat.",
                'confidence': 0.5,
                'sources': [],
                'num_sources': 0,
                'mode': 'conversational'
            }
    
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
        """Enhanced interactive mode with smart routing"""
        print("\n" + "=" * 60)
        print("EDITH Interactive Mode")
        print("=" * 60)
        print("Ask questions about your notes or just chat!")
        print("Commands: 'quit', 'summary', 'help'")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("\n💭 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                    print("\n👋 EDITH: Goodbye! Your notes are always here when you need them.")
                    break
                
                elif user_input.lower() == 'summary':
                    print("\n📊 Generating summary...")
                    summary = self.summarize()
                    print(f"\n{summary}")
                    continue
                
                elif user_input.lower() == 'help':
                    print("""
📚 EDITH Help:
- Ask questions about your notes (e.g., "What is polymorphism?")
- Have a conversation (e.g., "Hi EDITH", "Thanks!")
- Type 'summary' for a notes overview
- Type 'quit' to exit
                    """)
                    continue
                
                # Process query
                result = self.query(user_input)
                
                # Display answer with mode indicator
                mode_emoji = "🔍" if result.get('mode') == 'rag' else "💬"
                print(f"\n{mode_emoji} EDITH: {result['answer']}")
                
                # Show sources for RAG queries
                if result.get('mode') == 'rag' and result.get('num_sources', 0) > 0:
                    print(f"\n📎 Sources: {result['num_sources']} chunks (confidence: {result['confidence']:.2f})")
                    if result.get('sources'):
                        for source in result['sources'][:3]:  # Show top 3
                            print(f"   • {source.get('filename', 'Unknown')}")
                
            except KeyboardInterrupt:
                print("\n\n👋 EDITH: Interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {str(e)}")
                print(f"\n⚠️  EDITH: Sorry, I encountered an error: {str(e)}")


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
            
            # Show mode indicator
            mode_emoji = "🔍" if result.get('mode') == 'rag' else "💬"
            print(f"\n{mode_emoji} {result['answer']}\n")
            
            # Show sources for RAG queries
            if result.get('mode') == 'rag' and result.get('sources'):
                print(f"📎 Sources ({len(result['sources'])}):")
                for source in result['sources']:
                    print(f"  • {source['filename']}")
        
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