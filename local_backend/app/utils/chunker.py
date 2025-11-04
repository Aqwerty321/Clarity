"""
Text chunking utility with configurable size and overlap
"""
import os
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    TOKENIZER = tiktoken.get_encoding("cl100k_base")
    USE_TIKTOKEN = True
except ImportError:
    logger.warning("tiktoken not available, using approximate token counting")
    USE_TIKTOKEN = False
    TOKENIZER = None


def count_tokens(text: str) -> int:
    """
    Count tokens in text
    
    Args:
        text: Input text
        
    Returns:
        Token count
    """
    if USE_TIKTOKEN and TOKENIZER:
        return len(TOKENIZER.encode(text))
    else:
        # Approximate: 1 token ≈ 4 characters
        return len(text) // 4


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences (simple heuristic)
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitter (can be improved with spaCy)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[Tuple[str, int, int]]:
    """
    Chunk text with configurable size and overlap
    
    Args:
        text: Input text
        chunk_size: Target chunk size in tokens (default from env: 500)
        chunk_overlap: Overlap size in tokens (default from env: 100)
        
    Returns:
        List of tuples (chunk_text, start_char, end_char)
    """
    if chunk_size is None:
        chunk_size = int(os.getenv("CLARITY_CHUNK_SIZE", "500"))
    
    if chunk_overlap is None:
        chunk_overlap = int(os.getenv("CLARITY_CHUNK_OVERLAP", "100"))
    
    # Split into sentences for better boundaries
    sentences = split_into_sentences(text)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    char_start = 0
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        
        # If single sentence exceeds chunk size, split it by words
        if sentence_tokens > chunk_size:
            words = sentence.split()
            for word in words:
                word_tokens = count_tokens(word)
                
                if current_tokens + word_tokens > chunk_size and current_chunk:
                    # Save current chunk
                    chunk_text = " ".join(current_chunk)
                    char_end = char_start + len(chunk_text)
                    chunks.append((chunk_text, char_start, char_end))
                    
                    # Start new chunk with overlap
                    overlap_tokens = 0
                    overlap_chunk = []
                    for w in reversed(current_chunk):
                        w_tokens = count_tokens(w)
                        if overlap_tokens + w_tokens <= chunk_overlap:
                            overlap_chunk.insert(0, w)
                            overlap_tokens += w_tokens
                        else:
                            break
                    
                    current_chunk = overlap_chunk + [word]
                    current_tokens = overlap_tokens + word_tokens
                    char_start = char_end - len(" ".join(overlap_chunk))
                else:
                    current_chunk.append(word)
                    current_tokens += word_tokens
        
        # Add sentence to current chunk
        elif current_tokens + sentence_tokens <= chunk_size:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        else:
            # Save current chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                char_end = char_start + len(chunk_text)
                chunks.append((chunk_text, char_start, char_end))
                
                # Start new chunk with overlap
                overlap_tokens = 0
                overlap_chunk = []
                for s in reversed(current_chunk):
                    s_tokens = count_tokens(s)
                    if overlap_tokens + s_tokens <= chunk_overlap:
                        overlap_chunk.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                
                current_chunk = overlap_chunk + [sentence]
                current_tokens = overlap_tokens + sentence_tokens
                char_start = char_end - len(" ".join(overlap_chunk))
            else:
                current_chunk = [sentence]
                current_tokens = sentence_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        char_end = char_start + len(chunk_text)
        chunks.append((chunk_text, char_start, char_end))
    
    logger.info(f"Chunked text into {len(chunks)} chunks (size: {chunk_size}, overlap: {chunk_overlap})")
    
    return chunks
