"""
Tests for embedder service
"""
import pytest
from app.services.embedder import embedder


def test_embedder_initialization():
    """Test embedder initialization"""
    assert embedder is not None
    assert embedder.type in ["nomic", "sentence-transformers"]
    assert embedder.dimension > 0


def test_embed_single_text():
    """Test embedding a single text"""
    text = "This is a test sentence."
    embedding = embedder.embed_query(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == embedder.dimension
    assert all(isinstance(x, float) for x in embedding)


def test_embed_multiple_texts():
    """Test embedding multiple texts"""
    texts = [
        "First test sentence.",
        "Second test sentence.",
        "Third test sentence."
    ]
    embeddings = embedder.embed_texts(texts)
    
    assert len(embeddings) == len(texts)
    assert all(len(emb) == embedder.dimension for emb in embeddings)


def test_embed_empty_list():
    """Test embedding empty list"""
    embeddings = embedder.embed_texts([])
    assert embeddings == []


def test_embedding_similarity():
    """Test that similar texts have similar embeddings"""
    text1 = "Machine learning is a type of artificial intelligence."
    text2 = "Artificial intelligence includes machine learning."
    text3 = "The weather is nice today."
    
    emb1 = embedder.embed_query(text1)
    emb2 = embedder.embed_query(text2)
    emb3 = embedder.embed_query(text3)
    
    # Calculate cosine similarity
    import numpy as np
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_12 = cosine_similarity(emb1, emb2)
    sim_13 = cosine_similarity(emb1, emb3)
    
    # Similar texts should have higher similarity
    assert sim_12 > sim_13


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
