"""
ChromaDB service for vector storage and retrieval
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ChromaService:
    """Service for managing ChromaDB collections and queries"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize ChromaDB client
        
        Args:
            base_dir: Base directory for ChromaDB persistence (default: ~/.clarity/chroma/)
        """
        if base_dir is None:
            base_dir = os.path.expanduser(os.getenv("CLARITY_BASE_DIR", "~/.clarity"))
        
        self.chroma_dir = os.path.join(base_dir, "chroma")
        os.makedirs(self.chroma_dir, exist_ok=True)
        
        logger.info(f"Initializing ChromaDB at: {self.chroma_dir}")
        
        self.client = chromadb.PersistentClient(
            path=self.chroma_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    
    def get_collection_name(self, user_id: str) -> str:
        """
        Generate collection name for a user
        
        Args:
            user_id: Auth0 user ID (e.g., auth0|123456)
            
        Returns:
            Collection name (e.g., clarity_user__auth0_123456)
        """
        # Replace | with _ for collection name
        safe_user_id = user_id.replace("|", "_").replace("@", "_")
        return f"clarity_user__{safe_user_id}"
    
    def get_or_create_collection(self, user_id: str):
        """Get or create a collection for a user"""
        collection_name = self.get_collection_name(user_id)
        
        try:
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"user_id": user_id}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection
    
    def add_documents(
        self,
        user_id: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
        ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add documents to user's collection
        
        Args:
            user_id: Auth0 user ID
            documents: List of text chunks
            metadatas: List of metadata dicts
            embeddings: List of embedding vectors
            ids: Optional list of document IDs (auto-generated if None)
            
        Returns:
            Status dict with count
        """
        collection = self.get_or_create_collection(user_id)
        
        if ids is None:
            # Generate IDs
            existing_count = collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to collection {collection.name}")
        
        return {
            "status": "success",
            "count": len(documents),
            "collection": collection.name
        }
    
    def query(
        self,
        user_id: str,
        query_embedding: List[float],
        top_k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query user's collection
        
        Args:
            user_id: Auth0 user ID
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Query results with documents, distances, metadatas
        """
        try:
            collection = self.get_or_create_collection(user_id)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }
        
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {
                "documents": [],
                "distances": [],
                "metadatas": [],
                "ids": []
            }
    
    def delete_collection(self, user_id: str) -> bool:
        """Delete a user's collection"""
        collection_name = self.get_collection_name(user_id)
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def get_collection_count(self, user_id: str) -> int:
        """Get document count in user's collection"""
        try:
            collection = self.get_or_create_collection(user_id)
            return collection.count()
        except Exception:
            return 0


# Global instance
chroma_service = ChromaService()
