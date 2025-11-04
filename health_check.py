"""
Quick health check for Clarity dependencies
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "gpt-oss")

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            print(f"✅ Ollama is running at {OLLAMA_BASE_URL}")
            print(f"   Available models: {', '.join(model_names) if model_names else 'None'}")
            
            # Check for required models
            has_nomic = any("nomic" in name for name in model_names)
            has_gptoss = any("gpt-oss" in name for name in model_names)
            
            if EMBEDDING_MODEL == "nomic-embed-text":
                if has_nomic:
                    print(f"✅ Found nomic-embed-text for embeddings (768-dim)")
                else:
                    print(f"⚠️  nomic-embed-text not found. Run: ollama pull nomic-embed-text")
            
            if has_gptoss:
                print(f"✅ Found gpt-oss for LLM generation")
            else:
                print(f"⚠️  gpt-oss not found. Run: ollama pull gpt-oss")
            
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print(f"   Make sure Ollama is running: https://ollama.ai/")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def check_auth0():
    """Check if Auth0 is configured"""
    domain = os.getenv("VITE_AUTH0_DOMAIN")
    client_id = os.getenv("VITE_AUTH0_CLIENT_ID")
    
    if domain and domain != "YOUR-TENANT.auth0.com" and client_id and client_id != "YOUR_CLIENT_ID_HERE":
        print(f"✅ Auth0 configured: {domain}")
        return True
    else:
        print(f"⚠️  Auth0 not configured in .env")
        print(f"   Edit .env with your Auth0 credentials")
        return False

def check_python_packages():
    """Check if required Python packages are installed"""
    required = [
        "fastapi",
        "uvicorn",
        "chromadb",
        "requests",
        "pydantic",
        "dotenv"  # python-dotenv imports as 'dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    # Optional: Check sentence-transformers (only needed if Ollama fails)
    using_ollama = os.getenv("EMBEDDING_MODEL") == "nomic-embed-text"
    if using_ollama:
        print(f"   Using Ollama for embeddings (sentence-transformers optional)")
    else:
        try:
            __import__("sentence_transformers")
        except ImportError:
            print(f"   ⚠️  sentence-transformers not available (OK if using Ollama)")
    
    if not missing:
        print(f"✅ All core Python packages installed")
        return True
    else:
        print(f"⚠️  Missing Python packages: {', '.join(missing)}")
        print(f"   Run: pip install -r local_backend/requirements.txt")
        return False

def main():
    print("=" * 60)
    print("🔍 Clarity Health Check")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Ollama
    print("[1/3] Checking Ollama...")
    if not check_ollama():
        all_good = False
    print()
    
    # Check Auth0
    print("[2/3] Checking Auth0...")
    if not check_auth0():
        all_good = False
    print()
    
    # Check Python packages
    print("[3/3] Checking Python packages...")
    if not check_python_packages():
        all_good = False
    print()
    
    print("=" * 60)
    if all_good:
        print("✅ All checks passed! Ready to start Clarity.")
        print()
        print("Start the app:")
        print("  Backend:  cd local_backend && uvicorn app.main:app --reload")
        print("  Frontend: cd frontend && npm run dev")
        print()
        print("Or use the startup script:")
        print("  .\\infra\\scripts\\start_local.ps1")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
    print("=" * 60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
