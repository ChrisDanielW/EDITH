"""
Text Chunking Utilities for EDITH
Splits text into manageable chunks for embedding and retrieval
"""

import logging
from typing import List, Dict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextChunker:
    """Split text into chunks for processing"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to split
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of dictionaries containing chunks and metadata
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        
        # Try to split by paragraphs first
        paragraphs = self._split_by_paragraphs(text)
        
        current_chunk = ""
        chunk_num = 0
        
        for para in paragraphs:
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(self._create_chunk_dict(current_chunk, chunk_num, metadata))
                chunk_num += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + para
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Add the last chunk
        if current_chunk:
            chunks.append(self._create_chunk_dict(current_chunk, chunk_num, metadata))
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs"""
        # Split by double newlines or more
        paragraphs = re.split(r'\n\s*\n', text)
        # Filter out empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the last portion of text for overlap"""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Try to find a sentence boundary for clean overlap
        overlap_start = len(text) - self.chunk_overlap
        sentences = re.split(r'[.!?]\s+', text[overlap_start:])
        
        if len(sentences) > 1:
            # Start from the beginning of the last complete sentence
            return sentences[-1]
        
        return text[-self.chunk_overlap:]
    
    def _create_chunk_dict(self, text: str, chunk_num: int, metadata: Dict = None) -> Dict:
        """Create a dictionary for a chunk with metadata"""
        chunk_dict = {
            'text': text.strip(),
            'chunk_id': chunk_num,
            'char_count': len(text),
        }
        
        if metadata:
            chunk_dict['metadata'] = metadata
        
        return chunk_dict
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata'
            
        Returns:
            List of chunk dictionaries
        """
        all_chunks = []
        
        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            if text:
                chunks = self.chunk_text(text, metadata)
                all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks


class SmartChunker(TextChunker):
    """Advanced chunker that tries to split on semantic boundaries"""
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into semantically meaningful chunks
        
        Args:
            text: Text to split
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of dictionaries containing chunks and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split by sections (headers, if present)
        sections = self._split_by_sections(text)
        
        chunks = []
        chunk_num = 0
        
        for section in sections:
            # If section is small enough, keep it as one chunk
            if len(section) <= self.chunk_size:
                chunks.append(self._create_chunk_dict(section, chunk_num, metadata))
                chunk_num += 1
            else:
                # Split large sections further
                section_chunks = self._split_large_section(section)
                for chunk_text in section_chunks:
                    chunks.append(self._create_chunk_dict(chunk_text, chunk_num, metadata))
                    chunk_num += 1
        
        logger.info(f"Smart chunker created {len(chunks)} chunks")
        return chunks
    
    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by markdown-style headers or major breaks"""
        # Try to detect headers (lines starting with #, all caps, etc.)
        header_pattern = r'(?:^|\n)(?:#{1,6}\s+.+|[A-Z][A-Z\s]+:|\d+\.\s+[A-Z].+)(?:\n|$)'
        
        sections = []
        last_pos = 0
        
        for match in re.finditer(header_pattern, text):
            if match.start() > last_pos:
                sections.append(text[last_pos:match.start()].strip())
            last_pos = match.start()
        
        # Add the last section
        if last_pos < len(text):
            sections.append(text[last_pos:].strip())
        
        # If no sections found, return the whole text
        if not sections or len(sections) == 1:
            return self._split_by_paragraphs(text)
        
        return [s for s in sections if s]
    
    def _split_large_section(self, text: str) -> List[str]:
        """Split a large section into smaller chunks"""
        # Use the parent class method for splitting by paragraphs
        paragraphs = self._split_by_paragraphs(text)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + "\n\n" + para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
