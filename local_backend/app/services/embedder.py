"""
Embedder service with auto-fallback: Ollama (nomic) → sentence-transformers
"""
import os
from typing import List
import logging
import requests

logger = logging.getLogger(__name__)

# Configuration
EMBEDDER_TYPE = None
EMBEDDER_MODEL = None
EMBEDDING_DIM = 0
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Try Ollama first if using nomic-embed-text
if EMBEDDING_MODEL == "nomic-embed-text":
    try:
        # Test Ollama connection
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            EMBEDDER_TYPE = "ollama"
            EMBEDDER_MODEL = "nomic-embed-text"
            EMBEDDING_DIM = 768
            logger.info(f"✅ Using Ollama for embeddings: {EMBEDDER_MODEL} (768-dim)")
        else:
            raise ConnectionError("Ollama not responding")
    except Exception as e:
        logger.warning(f"Ollama not available ({e}), falling back to sentence-transformers")
        EMBEDDER_TYPE = None

# Fallback to sentence-transformers
if EMBEDDER_TYPE is None:
    # Don't import yet - will import on first use (lazy)
    EMBEDDER_TYPE = "sentence-transformers"
    EMBEDDER_MODEL = EMBEDDING_MODEL if EMBEDDING_MODEL != "nomic-embed-text" else "all-MiniLM-L6-v2"
    
    # Lazy load
    _model_instance = None
    
    def get_model():
        global _model_instance
        if _model_instance is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {EMBEDDER_MODEL}")
                _model_instance = SentenceTransformer(EMBEDDER_MODEL)
                EMBEDDING_DIM = _model_instance.get_sentence_embedding_dimension()
            except ImportError as e:
                logger.error(f"sentence-transformers not available: {e}")
                raise ImportError("No embedding library available! Start Ollama or install sentence-transformers.")
        return _model_instance
    
    logger.info(f"Fallback: sentence-transformers (will lazy-load if needed)")


class Embedder:
    """Unified embedder interface with auto-fallback"""
    
    def __init__(self):
        self.type = EMBEDDER_TYPE
        self.model_name = EMBEDDER_MODEL
        self.ollama_url = OLLAMA_BASE_URL
        
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed a list of texts
        
        Args:
            texts: List of strings to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.type == "ollama":
            # Use Ollama API for nomic-embed-text
            embeddings = []
            for text in texts:
                try:
                    response = requests.post(
                        f"{self.ollama_url}/api/embeddings",
                        json={
                            "model": self.model_name,
                            "prompt": text
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    embedding = response.json()["embedding"]
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Ollama embedding failed: {e}")
                    raise
            
            return embeddings
        
        elif self.type == "sentence-transformers":
            model = get_model()
            
            # Process in batches
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = model.encode(
                    batch,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                embeddings.extend(batch_embeddings.tolist())
            
            return embeddings
        
        else:
            raise ValueError(f"Unknown embedder type: {self.type}")
    
    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string"""
        return self.embed_texts([query])[0]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        if self.type == "ollama" and self.model_name == "nomic-embed-text":
            return 768
        elif self.type == "sentence-transformers":
            model = get_model()
            return model.get_sentence_embedding_dimension()
        elif self.type == "nomic":
            return 768
        return 0


# Global instance
embedder = Embedder()
