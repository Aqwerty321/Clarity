"""
System Verification Script for Clarity
Tests all components: Ollama, Backend, Environment
"""
import requests
import time
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 60)
print("CLARITY SYSTEM VERIFICATION")
print("=" * 60)

# 1. Check Environment Variables
print("\n1. ENVIRONMENT VARIABLES")
print("-" * 60)
env_vars = {
    "AUTH0_DOMAIN": os.getenv("AUTH0_DOMAIN"),
    "AUTH0_CLIENT_ID": os.getenv("AUTH0_CLIENT_ID"),
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL"),
    "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL"),
    "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
    "LLM_MODEL": os.getenv("LLM_MODEL"),
}

for key, value in env_vars.items():
    status = "✅" if value else "❌"
    print(f"{status} {key}: {value}")

# 2. Check Ollama Service
print("\n2. OLLAMA SERVICE")
print("-" * 60)
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    if r.status_code == 200:
        models = [m['name'] for m in r.json()['models']]
        print(f"✅ Ollama is running")
        print(f"   Installed models: {', '.join(models)}")
    else:
        print(f"❌ Ollama returned status {r.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to Ollama: {e}")

# 3. Test Ollama Embeddings
print("\n3. OLLAMA EMBEDDINGS (nomic-embed-text)")
print("-" * 60)
try:
    r = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": "test"},
        timeout=10
    )
    if r.status_code == 200:
        embedding = r.json()['embedding']
        dim = len(embedding)
        print(f"✅ Embeddings working")
        print(f"   Dimension: {dim} (expected: 768)")
        if dim == 768:
            print(f"   ✅ Correct dimension!")
        else:
            print(f"   ❌ Wrong dimension!")
    else:
        print(f"❌ Embedding request failed: {r.status_code}")
except Exception as e:
    print(f"❌ Embedding test failed: {e}")

# 4. Test Ollama LLM
print("\n4. OLLAMA LLM (gpt-oss:20b)")
print("-" * 60)
try:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gpt-oss:20b",
            "prompt": "What is 2+2? Reply with just the number.",
            "stream": False
        },
        timeout=30
    )
    if r.status_code == 200:
        response = r.json()['response']
        print(f"✅ LLM working")
        print(f"   Response: {response[:100]}")
    else:
        print(f"❌ LLM request failed: {r.status_code}")
except Exception as e:
    print(f"❌ LLM test failed: {e}")

# 5. Check Backend
print("\n5. BACKEND API (localhost:5000)")
print("-" * 60)
try:
    r = requests.get("http://localhost:5000/api/health", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Backend is running")
        print(f"   Status: {data.get('status')}")
        print(f"   Services: {data.get('services')}")
    else:
        print(f"❌ Backend returned status {r.status_code}")
except requests.exceptions.ConnectionError:
    print(f"❌ Cannot connect to backend - is it running?")
    print(f"   Start with: cd local_backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload")
except Exception as e:
    print(f"❌ Backend check failed: {e}")

# 6. Check Frontend Dependencies
print("\n6. FRONTEND")
print("-" * 60)
if os.path.exists("frontend/node_modules"):
    print("✅ Node modules installed")
else:
    print("❌ Node modules not found - run: cd frontend && npm install")

if os.path.exists("frontend/package.json"):
    print("✅ package.json exists")
else:
    print("❌ package.json not found")

# Summary
print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Ensure backend is running: cd local_backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload")
print("2. Start frontend: cd frontend && npm run dev")
print("3. Open browser: http://localhost:5173")
