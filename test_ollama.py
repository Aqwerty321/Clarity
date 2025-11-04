"""
Test Ollama integration with nomic-embed-text and gpt-oss
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def test_embedding():
    """Test nomic-embed-text embedding"""
    print("\n" + "="*60)
    print("🧮 Testing nomic-embed-text Embedding")
    print("="*60)
    
    test_text = "Neural networks are computational models inspired by the human brain."
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": test_text
            },
            timeout=30
        )
        response.raise_for_status()
        
        embedding = response.json()["embedding"]
        
        print(f"✅ Successfully generated embedding")
        print(f"   Text: \"{test_text[:50]}...\"")
        print(f"   Dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        if len(embedding) == 768:
            print(f"✅ Correct dimension (768) for nomic-embed-text")
            return True
        else:
            print(f"⚠️  Expected 768 dimensions, got {len(embedding)}")
            return False
            
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return False

def test_generation():
    """Test gpt-oss text generation"""
    print("\n" + "="*60)
    print("🤖 Testing gpt-oss Text Generation")
    print("="*60)
    
    test_prompt = "Explain what a neural network is in one sentence."
    
    try:
        print(f"   Prompt: \"{test_prompt}\"")
        print(f"   Generating... (this may take a few seconds)")
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": test_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100
                }
            },
            timeout=60
        )
        response.raise_for_status()
        
        generated_text = response.json()["response"]
        
        print(f"✅ Successfully generated text")
        print(f"   Response: \"{generated_text.strip()}\"")
        
        if len(generated_text.strip()) > 0:
            return True
        else:
            print(f"⚠️  Generated empty response")
            return False
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

def test_rag_pipeline():
    """Test complete RAG pipeline simulation"""
    print("\n" + "="*60)
    print("🔄 Testing Complete RAG Pipeline")
    print("="*60)
    
    # Simulate RAG workflow
    documents = [
        "A neural network is a computational model inspired by biological neural networks.",
        "Neural networks consist of interconnected nodes organized in layers.",
        "Training a neural network involves adjusting connection weights through backpropagation."
    ]
    
    query = "What is a neural network?"
    
    print(f"   Documents: {len(documents)} chunks")
    print(f"   Query: \"{query}\"")
    print()
    
    # Step 1: Embed documents
    print("   [1/4] Embedding documents...")
    doc_embeddings = []
    for i, doc in enumerate(documents):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": doc
                },
                timeout=30
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]
            doc_embeddings.append(embedding)
            print(f"         ✅ Document {i+1} embedded ({len(embedding)} dim)")
        except Exception as e:
            print(f"         ❌ Document {i+1} failed: {e}")
            return False
    
    # Step 2: Embed query
    print("   [2/4] Embedding query...")
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": query
            },
            timeout=30
        )
        response.raise_for_status()
        query_embedding = response.json()["embedding"]
        print(f"         ✅ Query embedded ({len(query_embedding)} dim)")
    except Exception as e:
        print(f"         ❌ Query embedding failed: {e}")
        return False
    
    # Step 3: Compute similarity (simple dot product)
    print("   [3/4] Computing similarity...")
    similarities = []
    for i, doc_emb in enumerate(doc_embeddings):
        similarity = sum(a * b for a, b in zip(query_embedding, doc_emb))
        similarities.append((i, similarity))
        print(f"         Document {i+1}: similarity = {similarity:.4f}")
    
    # Get top document
    top_idx = max(similarities, key=lambda x: x[1])[0]
    print(f"         ✅ Most relevant: Document {top_idx+1}")
    
    # Step 4: Generate answer with context
    print("   [4/4] Generating answer with RAG...")
    context = documents[top_idx]
    rag_prompt = f"""Context: {context}

Question: {query}

Answer (in one sentence):"""
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": rag_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100
                }
            },
            timeout=60
        )
        response.raise_for_status()
        answer = response.json()["response"].strip()
        
        print(f"         ✅ Answer generated:")
        print(f"         \"{answer}\"")
        print()
        
        return True
    except Exception as e:
        print(f"         ❌ Answer generation failed: {e}")
        return False

def main():
    print("="*60)
    print("🧪 Ollama Integration Test Suite")
    print("="*60)
    print(f"   Ollama URL: {OLLAMA_BASE_URL}")
    print()
    
    results = []
    
    # Test 1: Embedding
    results.append(("Embedding (nomic-embed-text)", test_embedding()))
    
    # Test 2: Generation
    results.append(("Generation (gpt-oss)", test_generation()))
    
    # Test 3: RAG Pipeline
    results.append(("Complete RAG Pipeline", test_rag_pipeline()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print("="*60)
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("✅ All tests passed! Clarity is ready to use with Ollama.")
        print()
        print("Next steps:")
        print("  1. Start backend: cd local_backend && uvicorn app.main:app --reload")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Open: http://localhost:5173")
        return 0
    else:
        print("⚠️  Some tests failed. Please check Ollama setup.")
        print()
        print("Troubleshooting:")
        print("  1. Ensure Ollama is running: ollama serve")
        print("  2. Pull models: ollama pull nomic-embed-text && ollama pull gpt-oss")
        print("  3. Check Ollama: curl http://localhost:11434/api/tags")
        return 1

if __name__ == "__main__":
    sys.exit(main())
