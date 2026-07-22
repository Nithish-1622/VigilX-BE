import re
from typing import List, Dict, Any

class TextProcessingEngine:
    """
    Handles chunking, entity extraction, and NLP prep for unstructured text.
    """
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Splits long text into overlapping chunks for embedding.
        Simple token heuristic: ~4 chars per token.
        """
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract basic keywords (for BM25/hybrid search metadata).
        This is a rudimentary implementation; would use NLTK/Spacy in prod.
        """
        # Remove punctuation
        clean = re.sub(r'[^\w\s]', '', text.lower())
        words = clean.split()
        # Basic stopword filter
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        # Return unique
        return list(set(keywords))

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate number of LLM tokens."""
        return len(text.split()) * 4 // 3

    @staticmethod
    def extract_metadata(text: str) -> Dict[str, Any]:
        """Extract basic text metadata."""
        return {
            "char_count": len(text),
            "word_count": len(text.split()),
            "estimated_tokens": TextProcessingEngine.estimate_tokens(text),
            "keywords": TextProcessingEngine.extract_keywords(text)[:20]
        }
