"""
RAG Service for EDITH
Handles Retrieval-Augmented Generation workflow
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGService:
    """Manages the RAG pipeline for EDITH"""
    
    def __init__(
        self,
        vector_store,
        llama_client,
        embedding_generator,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize RAG service
        
        Args:
            vector_store: VectorStore instance
            llama_client: LlamaClient instance
            embedding_generator: EmbeddingGenerator instance
            top_k: Number of relevant documents to retrieve
            similarity_threshold: Minimum similarity score for retrieval
        """
        self.vector_store = vector_store
        self.llama_client = llama_client
        self.embedding_generator = embedding_generator
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
    
    def query(
        self,
        question: str,
        filter_metadata: Optional[Dict] = None,
        max_context_length: int = 2000
    ) -> Dict[str, any]:
        """
        Query the knowledge base and generate an answer
        
        Args:
            question: User's question
            filter_metadata: Optional metadata filters for retrieval
            max_context_length: Maximum characters for context
            
        Returns:
            Dictionary containing answer, sources, and metadata
        """
        try:
            # 1. Generate embedding for the question
            logger.info(f"Processing query: {question[:50]}...")
            question_embedding = self.embedding_generator.generate_embeddings(question)
            
            # 2. Retrieve relevant documents from vector store
            results = self.vector_store.query_vectors(
                query_vector=question_embedding,
                top_k=self.top_k,
                filter_dict=filter_metadata,
                include_metadata=True
            )
            
            # 3. Filter by similarity threshold
            logger.info(f"Retrieved {len(results)} results with scores: {[r['score'] for r in results[:3]]}")
            relevant_results = [
                r for r in results
                if r['score'] >= self.similarity_threshold
            ]
            logger.info(f"After filtering with threshold {self.similarity_threshold}: {len(relevant_results)} relevant results")
            
            if not relevant_results:
                return {
                    'answer': "I couldn't find relevant information in your notes to answer this question.",
                    'sources': [],
                    'confidence': 0.0,
                    'num_sources': 0
                }
            
            # 4. Prepare context from retrieved documents
            context = self._prepare_context(relevant_results, max_length=max_context_length)
            logger.debug(f"Context preview (first 500 chars): {context[:500]}...")
            
            # 5. Generate answer using LLaMA with context (succinct mode)
            answer = self.llama_client.chat(
                message=question,
                context=context,
                system_prompt="""You are EDITH, a precise and helpful AI assistant.
When answering from provided context:
- Be direct and concise (2-3 sentences max unless asked for details)
- Use bullet points for lists
- If the answer is in the context, state it clearly
- If uncertain or info missing, say so briefly
- Don't add information not in the context"""
            )
            
            # 6. Prepare sources information
            sources = self._extract_sources(relevant_results)
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': relevant_results[0]['score'] if relevant_results else 0.0,
                'num_sources': len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            return {
                'answer': f"An error occurred while processing your question: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'num_sources': 0
            }
    
    def summarize_notes(
        self,
        filter_metadata: Optional[Dict] = None,
        summary_style: str = "comprehensive"
    ) -> str:
        """
        Generate a summary of notes based on filters
        
        Args:
            filter_metadata: Optional metadata filters
            summary_style: Style of summary (comprehensive, bullet, brief)
            
        Returns:
            Summary text
        """
        try:
            # Get some representative documents
            # We'll use a generic query to get a sample
            sample_embedding = self.embedding_generator.generate_embeddings(
                "main topics themes key points summary"
            )
            
            results = self.vector_store.query_vectors(
                query_vector=sample_embedding,
                top_k=10,
                filter_dict=filter_metadata,
                include_metadata=True
            )
            
            if not results:
                return "No notes found to summarize."
            
            # Prepare context
            context = self._prepare_context(results, max_length=3000)
            
            # Create summary prompt based on style
            style_prompts = {
                'comprehensive': "Create a detailed, comprehensive summary of the following notes, covering all main topics and key points.",
                'bullet': "Create a bullet-point summary of the key points from the following notes.",
                'brief': "Create a brief, concise summary of the main ideas in the following notes."
            }
            
            prompt = style_prompts.get(summary_style, style_prompts['comprehensive'])
            
            summary = self.llama_client.chat(
                message=prompt,
                context=context,
                system_prompt="You are EDITH, an AI assistant specialized in creating clear, well-organized summaries of notes."
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def _prepare_context(self, results: List[Dict], max_length: int) -> str:
        """
        Prepare context from retrieved results
        
        Args:
            results: List of retrieved documents
            max_length: Maximum character length for context
            
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results):
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            # Format the chunk with source information
            source_info = f"[Source: {metadata.get('filename', 'Unknown')}]"
            chunk_text = f"{source_info}\n{text}\n"
            
            # Check if adding this chunk would exceed max length
            if current_length + len(chunk_text) > max_length:
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n---\n".join(context_parts)
    
    def _extract_sources(self, results: List[Dict]) -> List[Dict]:
        """
        Extract source information from results
        
        Args:
            results: List of retrieved documents
            
        Returns:
            List of source dictionaries
        """
        sources = []
        seen_files = set()
        
        for result in results:
            metadata = result.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            
            if filename not in seen_files:
                sources.append({
                    'filename': filename,
                    'relevance_score': result['score'],
                    'type': metadata.get('type', 'unknown')
                })
                seen_files.add(filename)
        
        return sources
    
    def analyze_note(self, note_text: str) -> Dict[str, any]:
        """
        Analyze a single note and extract key information
        
        Args:
            note_text: Text content of the note
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis_prompt = """Analyze the following note and provide:
1. Main topics/themes
2. Key points or takeaways
3. Any action items or important dates
4. Overall category or subject area

Note:"""
            
            analysis = self.llama_client.chat(
                message=analysis_prompt,
                context=note_text,
                system_prompt="You are EDITH, an AI assistant that analyzes notes to extract structured information."
            )
            
            return {
                'success': True,
                'analysis': analysis,
                'note_length': len(note_text)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing note: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
