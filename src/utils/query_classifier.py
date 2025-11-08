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
    
    # Strong conversational signals (should NOT use RAG)
    STRONG_CONVERSATIONAL = [
        # Greetings
        r'\b(hi|hello|hey|hiya|sup|yo|greetings)\b',
        r'\bgood (morning|afternoon|evening|night)\b',
        # Gratitude
        r'\b(thanks?|thank you|thx|ty)\b',
        # Farewells
        r'\b(bye|goodbye|see you|later|cya)\b',
        # Social
        r'\bhow are you\b',
        r'\bnice to (meet|talk|chat)',
        r'\b(okay|ok|cool|great|awesome|nice|sweet)\b$',
        # Identity questions about EDITH herself
        r'\b(who|what) are you\b',
        r'\byour name\b',
        r'\btell me about yourself\b',
        # Casual affirmations/reactions
        r'^(yeah|yep|nope|nah|sure|exactly|right)$',
    ]
    
    # Strong knowledge-seeking signals (MUST use RAG)
    STRONG_KNOWLEDGE = [
        # Direct information requests
        r'\b(what|explain|define|describe) (is|are|the|a)\b',
        r'\b(how|why) (do|does|did|can|should)\b',
        r'\b(tell me about|show me|find|search for)\b',
        r'\b(give me|provide) (information|details|example)\b',
        # List/comparison requests
        r'\b(list|enumerate|compare|difference between)\b',
        # Note-specific
        r'\b(in (my|the) notes|according to|from (my|the) (notes|documents))\b',
        r'\b(summarize|summary of)\b',
    ]
    
    # Weak knowledge indicators
    KNOWLEDGE_TERMS = [
        'concept', 'theory', 'principle', 'method', 'technique',
        'definition', 'meaning', 'purpose', 'function', 'process',
        'advantage', 'disadvantage', 'benefit', 'drawback',
        'example', 'instance', 'case', 'scenario'
    ]
    
    def __init__(self):
        """Initialize query classifier"""
        self.strong_conv_patterns = [re.compile(p, re.IGNORECASE) for p in self.STRONG_CONVERSATIONAL]
        self.strong_know_patterns = [re.compile(p, re.IGNORECASE) for p in self.STRONG_KNOWLEDGE]
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
        
        # Check for explicit override
        if "don't look at" in query_lower or "without database" in query_lower or "just chat" in query_lower:
            return {
                'type': 'conversational',
                'confidence': 1.0,
                'reason': "User explicitly requested conversational mode"
            }
        
        # Check strong conversational patterns
        for pattern in self.strong_conv_patterns:
            if pattern.search(query_lower):
                return {
                    'type': 'conversational',
                    'confidence': 0.95,
                    'reason': f"Strong conversational pattern detected: {pattern.pattern}"
                }
        
        # Check strong knowledge patterns
        for pattern in self.strong_know_patterns:
            if pattern.search(query_lower):
                return {
                    'type': 'knowledge',
                    'confidence': 0.95,
                    'reason': f"Strong knowledge-seeking pattern detected: {pattern.pattern}"
                }
        
        # Scoring for ambiguous cases
        knowledge_score = self._score_knowledge(query_lower)
        conversational_score = self._score_conversational(query_lower)
        
        # Decision logic
        if conversational_score >= 2:
            return {
                'type': 'conversational',
                'confidence': 0.75,
                'reason': "Primarily conversational tone"
            }
        elif knowledge_score >= 3:
            return {
                'type': 'knowledge',
                'confidence': 0.80,
                'reason': "Multiple knowledge indicators present"
            }
        elif knowledge_score > 0:
            return {
                'type': 'knowledge',
                'confidence': 0.60,
                'reason': "Appears to be seeking information"
            }
        else:
            # Very short or unclear - default to conversational to be natural
            if len(query_lower.split()) <= 4:
                return {
                    'type': 'conversational',
                    'confidence': 0.65,
                    'reason': "Short query, defaulting to conversational"
                }
            else:
                return {
                    'type': 'knowledge',
                    'confidence': 0.55,
                    'reason': "Longer query, likely seeking information"
                }
    
    def _score_knowledge(self, query: str) -> int:
        """Score how much query looks like knowledge-seeking"""
        score = 0
        
        # Check for knowledge terms
        for term in self.KNOWLEDGE_TERMS:
            if term in query:
                score += 1
        
        # Question marks suggest queries
        if '?' in query:
            score += 1
        
        # Wh- questions (what, why, how, when, where)
        if re.search(r'\b(what|why|how|when|where|which)\b', query):
            score += 2
        
        # Technical/academic language patterns
        if re.search(r'\b\w+tion\b', query):  # words ending in -tion
            score += 1
        
        return score
    
    def _score_conversational(self, query: str) -> int:
        """Score how conversational the query is"""
        score = 0
        
        # Very short queries
        word_count = len(query.split())
        if word_count <= 2:
            score += 2
        elif word_count == 3:
            score += 1
        
        # Casual language
        casual_words = ['like', 'kinda', 'sorta', 'maybe', 'just', 'really', 'pretty', 'quite']
        for word in casual_words:
            if f' {word} ' in f' {query} ':
                score += 1
        
        # Exclamation marks (excitement/casual tone)
        if '!' in query:
            score += 1
        
        # No question mark but very short
        if '?' not in query and word_count <= 3:
            score += 1
        
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
