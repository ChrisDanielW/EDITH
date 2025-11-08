"""
Query Classifier for EDITH
Determines if a query needs RAG retrieval or just conversation
"""

from typing import Dict, Literal
import re
import logging

logger = logging.getLogger(__name__)


class QueryClassifier:
    """Classifies queries as 'knowledge', 'conversational', or 'hybrid'"""
    
    # Keywords that suggest knowledge queries
    KNOWLEDGE_KEYWORDS = [
        'what', 'how', 'why', 'when', 'where', 'who',
        'explain', 'define', 'describe', 'tell me about',
        'summarize', 'list', 'compare', 'difference',
        'example', 'meaning', 'purpose', 'concept',
        'notes', 'document', 'information about',
        'show me', 'find', 'search', 'look up'
    ]
    
    # Keywords that suggest conversational queries
    CONVERSATIONAL_KEYWORDS = [
        'hello', 'hi', 'hey', 'thanks', 'thank you',
        'bye', 'goodbye', 'okay', 'ok', 'cool',
        'nice', 'great', 'awesome', 'how are you',
        'who are you', 'your name', 'help me',
        'good morning', 'good evening', 'good night'
    ]
    
    def __init__(self):
        """Initialize query classifier"""
        logger.info("Query classifier initialized")
    
    def classify(self, query: str) -> Dict[str, any]:
        """
        Classify a query and return classification info
        
        Args:
            query: User's input query
            
        Returns:
            Dict with 'type', 'confidence', and 'reason'
        """
        query_lower = query.lower().strip()
        
        # Rule-based classification
        knowledge_score = self._score_knowledge(query_lower)
        conversational_score = self._score_conversational(query_lower)
        
        # Determine type
        if knowledge_score > conversational_score and knowledge_score > 2:
            query_type = 'knowledge'
            confidence = min(knowledge_score / 5, 1.0)
            reason = "Contains knowledge-seeking keywords"
        elif conversational_score > knowledge_score:
            query_type = 'conversational'
            confidence = min(conversational_score / 3, 1.0)
            reason = "Contains conversational patterns"
        elif knowledge_score > 0:
            query_type = 'hybrid'
            confidence = 0.5
            reason = "Mixed conversational and knowledge query"
        else:
            # Default to knowledge if uncertain
            query_type = 'knowledge'
            confidence = 0.3
            reason = "Defaulting to knowledge search"
        
        return {
            'type': query_type,
            'confidence': confidence,
            'reason': reason,
            'scores': {
                'knowledge': knowledge_score,
                'conversational': conversational_score
            }
        }
    
    def _score_knowledge(self, query: str) -> int:
        """Score how much query looks like knowledge-seeking"""
        score = 0
        
        # Check for knowledge keywords
        for keyword in self.KNOWLEDGE_KEYWORDS:
            if keyword in query:
                score += 1
        
        # Question marks suggest queries
        if '?' in query:
            score += 1
        
        # Longer queries are usually knowledge-seeking
        if len(query.split()) > 5:
            score += 1
        
        return score
    
    def _score_conversational(self, query: str) -> int:
        """Score how conversational the query is"""
        score = 0
        
        # Check for conversational keywords
        for keyword in self.CONVERSATIONAL_KEYWORDS:
            if keyword in query:
                score += 2  # Weight conversational higher
        
        # Very short queries are often conversational
        if len(query.split()) <= 3 and '?' not in query:
            score += 1
        
        # Greetings at start
        if query.startswith(('hi', 'hello', 'hey', 'yo', 'sup')):
            score += 2
        
        return score
    
    def should_use_rag(self, query: str, threshold: float = 0.4) -> bool:
        """
        Quick check if RAG should be used
        
        Args:
            query: User query
            threshold: Confidence threshold for using RAG
            
        Returns:
            True if RAG should be used
        """
        classification = self.classify(query)
        
        # Use RAG for knowledge and hybrid queries above threshold
        if classification['type'] in ['knowledge', 'hybrid']:
            return classification['confidence'] >= threshold
        
        return False
