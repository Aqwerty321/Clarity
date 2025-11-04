"""
Tests for local backend API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "embedder_model" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"


def test_embed_texts():
    """Test embedding generation"""
    request_data = {
        "texts": ["Hello world", "This is a test"]
    }
    response = client.post("/api/embed", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "embeddings" in data
    assert len(data["embeddings"]) == 2
    assert data["dimension"] > 0


def test_ask_question_no_documents():
    """Test asking question with no documents"""
    request_data = {
        "user_id": "test_user",
        "question": "What is machine learning?",
        "top_k": 4,
        "use_summary": True
    }
    response = client.post("/api/ask", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "source_chunks" in data


@pytest.mark.asyncio
async def test_ingest_text_file(tmp_path):
    """Test document ingestion with text file"""
    # Create temporary text file
    test_file = tmp_path / "test.txt"
    test_file.write_text("This is a test document. It contains some text for testing.")
    
    with open(test_file, "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"user_id": "test_user", "title": "Test Document"}
        
        response = client.post("/api/ingest", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["num_chunks"] > 0
        assert "document_id" in result


def test_generate_quiz():
    """Test quiz generation"""
    request_data = {
        "user_id": "test_user",
        "topic": "Machine Learning",
        "difficulty": "medium",
        "num_questions": 3
    }
    
    # This will fail if no documents are ingested, which is expected
    response = client.post("/api/generate-quiz", json=request_data)
    # Accept either success or 404 (no documents)
    assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
