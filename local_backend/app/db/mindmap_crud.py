"""
CRUD operations for mind maps
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .mindmap_models import MindMap
import uuid


def get_mind_maps(db: Session, user_id: str) -> List[MindMap]:
    """Get all mind maps for a user"""
    return db.query(MindMap).filter(MindMap.user_id == user_id).all()


def get_mind_map(db: Session, mind_map_id: str, user_id: str) -> Optional[MindMap]:
    """Get a specific mind map"""
    return db.query(MindMap).filter(
        MindMap.id == mind_map_id,
        MindMap.user_id == user_id
    ).first()


def create_mind_map(
    db: Session,
    user_id: str,
    title: str,
    notebook_id: str,
    description: Optional[str] = None,
    max_depth: int = 3
) -> MindMap:
    """Create a new mind map"""
    mind_map = MindMap(
        id=str(uuid.uuid4()),
        user_id=user_id,
        notebook_id=notebook_id,
        title=title,
        description=description,
        max_depth=max_depth,
        nodes=[],
        edges=[]
    )
    db.add(mind_map)
    db.commit()
    db.refresh(mind_map)
    return mind_map


def update_mind_map_data(
    db: Session,
    mind_map_id: str,
    nodes: list,
    edges: list,
    node_count: int,
    depth: int
) -> Optional[MindMap]:
    """Update mind map with generated nodes and edges"""
    mind_map = db.query(MindMap).filter(MindMap.id == mind_map_id).first()
    if mind_map:
        mind_map.nodes = nodes
        mind_map.edges = edges
        mind_map.node_count = node_count
        mind_map.depth = depth
        db.commit()
        db.refresh(mind_map)
    return mind_map


def delete_mind_map(db: Session, mind_map_id: str, user_id: str) -> bool:
    """Delete a mind map"""
    mind_map = get_mind_map(db, mind_map_id, user_id)
    if mind_map:
        db.delete(mind_map)
        db.commit()
        return True
    return False
