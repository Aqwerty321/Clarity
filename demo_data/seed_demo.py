"""
Script to seed demo data into ChromaDB
This creates a demo user and ingests sample documents
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "local_backend"))

from app.services.embedder import embedder
from app.services.chroma_service import chroma_service
from app.utils.chunker import chunk_text

# Demo user ID
DEMO_USER_ID = "demo_user_123"

def seed_demo_data():
    """Seed demo documents into ChromaDB"""
    print("🌱 Seeding demo data...")
    
    # Path to demo data
    demo_data_dir = Path(__file__).parent.parent / "demo_data"
    
    # List of demo files
    demo_files = [
        "machine_learning_basics.md",
        "deep_learning_fundamentals.md"
    ]
    
    for filename in demo_files:
        filepath = demo_data_dir / filename
        
        if not filepath.exists():
            print(f"⚠️  File not found: {filename}")
            continue
        
        print(f"📄 Processing {filename}...")
        
        # Read file
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Chunk text
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=100)
        print(f"   Created {len(chunks)} chunks")
        
        # Extract chunk texts
        chunk_texts = [chunk[0] for chunk in chunks]
        
        # Generate embeddings
        print(f"   Generating embeddings...")
        embeddings = embedder.embed_texts(chunk_texts)
        
        # Prepare metadata
        metadatas = [
            {
                "document_id": f"demo_{filename}",
                "title": filename.replace("_", " ").replace(".md", "").title(),
                "chunk_index": i,
                "char_start": chunk[1],
                "char_end": chunk[2],
                "source": "demo"
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Store in ChromaDB
        print(f"   Storing in ChromaDB...")
        chroma_service.add_documents(
            user_id=DEMO_USER_ID,
            documents=chunk_texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        print(f"✅ Ingested {filename}")
    
    # Print summary
    collection_count = chroma_service.get_collection_count(DEMO_USER_ID)
    print(f"\n🎉 Demo data seeded successfully!")
    print(f"   Total chunks: {collection_count}")
    print(f"   Demo user ID: {DEMO_USER_ID}")


if __name__ == "__main__":
    seed_demo_data()
