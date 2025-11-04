"""
Tests for chunker utility
"""
import pytest
from app.utils.chunker import chunk_text, count_tokens


def test_count_tokens():
    """Test token counting"""
    text = "This is a simple test."
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_chunk_small_text():
    """Test chunking small text"""
    text = "This is a short text that should result in a single chunk."
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    
    assert len(chunks) >= 1
    assert all(isinstance(chunk, tuple) for chunk in chunks)
    assert all(len(chunk) == 3 for chunk in chunks)  # (text, start, end)


def test_chunk_large_text():
    """Test chunking large text"""
    text = " ".join(["This is sentence number {}.".format(i) for i in range(100)])
    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
    
    assert len(chunks) > 1
    
    # Check that chunks have overlap
    if len(chunks) > 1:
        first_chunk = chunks[0][0]
        second_chunk = chunks[1][0]
        # Some words from first chunk should appear in second chunk
        first_words = set(first_chunk.split()[-5:])
        second_words = set(second_chunk.split()[:10])
        assert len(first_words & second_words) > 0


def test_chunk_boundaries():
    """Test that chunks respect character boundaries"""
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunk_text(text, chunk_size=20, chunk_overlap=5)
    
    for chunk_text, start, end in chunks:
        assert end > start
        assert len(chunk_text) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
