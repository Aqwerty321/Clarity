"""
Mind Map API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
import json

from ..db.database import get_db
from ..db import mindmap_crud, crud
from ..db.mindmap_models import MindMap
from ..services.llm_wrapper import llm_wrapper
from ..services.chroma_service import ChromaService
from ..services.embedder import Embedder

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
chroma_service = ChromaService()
embedder = Embedder()


# Pydantic models
class MindMapCreate(BaseModel):
    user_id: str
    title: str
    notebook_id: str
    description: Optional[str] = None
    max_depth: int = 3


class MindMapResponse(BaseModel):
    id: str
    user_id: str
    notebook_id: Optional[str]
    title: str
    description: Optional[str]
    max_depth: int
    node_count: int
    depth: int
    nodes: list
    edges: list
    notebookTitle: Optional[str] = None
    created_at: str
    updated_at: str


@router.get("/mind-maps")
async def get_mind_maps(user_id: str, db: Session = Depends(get_db)):
    """Get all mind maps for a user"""
    try:
        mind_maps = mindmap_crud.get_mind_maps(db, user_id)
        
        # Enrich with notebook titles
        result = []
        for mind_map in mind_maps:
            mind_map_dict = {
                "id": mind_map.id,
                "user_id": mind_map.user_id,
                "notebook_id": mind_map.notebook_id,
                "title": mind_map.title,
                "description": mind_map.description,
                "max_depth": mind_map.max_depth,
                "node_count": mind_map.node_count,
                "depth": mind_map.depth,
                "nodes": mind_map.nodes or [],
                "edges": mind_map.edges or [],
                "created_at": mind_map.created_at.isoformat() if mind_map.created_at else None,
                "updated_at": mind_map.updated_at.isoformat() if mind_map.updated_at else None,
            }
            
            # Get notebook title if linked
            if mind_map.notebook_id:
                notebook = crud.get_notebook(db, mind_map.notebook_id, user_id)
                if notebook:
                    mind_map_dict["notebookTitle"] = notebook.title
            
            result.append(mind_map_dict)
        
        return result
    except Exception as e:
        logger.error(f"Failed to get mind maps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mind-maps")
async def create_mind_map(mind_map_data: MindMapCreate, db: Session = Depends(get_db)):
    """Create a new mind map and generate it from notebook content"""
    try:
        # Verify notebook exists
        notebook = crud.get_notebook(db, mind_map_data.notebook_id, mind_map_data.user_id)
        if not notebook:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        # Create mind map
        mind_map = mindmap_crud.create_mind_map(
            db=db,
            user_id=mind_map_data.user_id,
            title=mind_map_data.title,
            notebook_id=mind_map_data.notebook_id,
            description=mind_map_data.description,
            max_depth=mind_map_data.max_depth
        )
        
        logger.info(f"Created mind map {mind_map.id} for user {mind_map_data.user_id}")
        
        # Generate mind map data from notebook
        await generate_mind_map_data(db, mind_map.id, mind_map_data.user_id, mind_map_data.notebook_id, mind_map_data.max_depth)
        
        # Reload with generated data
        mind_map = mindmap_crud.get_mind_map(db, mind_map.id, mind_map_data.user_id)
        
        return {
            "id": mind_map.id,
            "user_id": mind_map.user_id,
            "notebook_id": mind_map.notebook_id,
            "title": mind_map.title,
            "description": mind_map.description,
            "max_depth": mind_map.max_depth,
            "node_count": mind_map.node_count,
            "depth": mind_map.depth,
            "nodes": mind_map.nodes or [],
            "edges": mind_map.edges or [],
            "created_at": mind_map.created_at.isoformat() if mind_map.created_at else None,
            "updated_at": mind_map.updated_at.isoformat() if mind_map.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create mind map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mind-maps/{mind_map_id}")
async def get_mind_map(mind_map_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get a specific mind map"""
    try:
        mind_map = mindmap_crud.get_mind_map(db, mind_map_id, user_id)
        if not mind_map:
            raise HTTPException(status_code=404, detail="Mind map not found")
        
        return {
            "id": mind_map.id,
            "user_id": mind_map.user_id,
            "notebook_id": mind_map.notebook_id,
            "title": mind_map.title,
            "description": mind_map.description,
            "max_depth": mind_map.max_depth,
            "node_count": mind_map.node_count,
            "depth": mind_map.depth,
            "nodes": mind_map.nodes or [],
            "edges": mind_map.edges or [],
            "created_at": mind_map.created_at.isoformat() if mind_map.created_at else None,
            "updated_at": mind_map.updated_at.isoformat() if mind_map.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get mind map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/mind-maps/{mind_map_id}")
async def delete_mind_map(mind_map_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete a mind map"""
    try:
        success = mindmap_crud.delete_mind_map(db, mind_map_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Mind map not found")
        
        logger.info(f"Deleted mind map {mind_map_id}")
        return {"status": "success", "message": "Mind map deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete mind map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_mind_map_data(db: Session, mind_map_id: str, user_id: str, notebook_id: str, max_depth: int = 3):
    """Generate mind map nodes and edges using LLM and ChromaDB"""
    try:
        # Get collection for notebook
        collection_name = f"clarity_user__{user_id.replace('|', '_')}__{notebook_id}"
        
        # Try to get the collection using the ChromaDB client
        try:
            collection = chroma_service.client.get_collection(name=collection_name)
        except Exception as e:
            logger.warning(f"No collection found for notebook {notebook_id}: {e}")
            return
        
        # Generate query embedding using our embedder
        query_text = "main topics, key concepts, important ideas, central themes"
        query_embedding = embedder.embed_query(query_text)
        
        # Query for main topics using embeddings - get more context for detailed mind maps
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=30
        )
        
        if not results or not results.get('documents') or not results['documents'][0]:
            logger.warning(f"No documents found in collection for notebook {notebook_id}")
            return
        
        # Prepare context from documents - use more docs for richer content
        context_docs = results['documents'][0][:25]
        context = "\n\n".join(context_docs)
        
        # Generate depth level list for prompt
        depth_levels = ", ".join([str(i) for i in range(max_depth + 1)])
        
        # Calculate expected node counts based on max_depth
        # Base formula: roughly 3-5x nodes at each level (exponential growth)
        total_nodes = 30 + (max_depth * 8)  # Scale with depth
        
        # Build dynamic node distribution guide
        depth_distribution = []
        depth_distribution.append("   - Depth 0 (root): 1 node (main central topic)")
        if max_depth >= 1:
            depth_distribution.append("   - Depth 1: 4-6 nodes (major subtopics/categories)")
        if max_depth >= 2:
            depth_distribution.append("   - Depth 2: 8-12 nodes (detailed concepts/mechanisms)")
        if max_depth >= 3:
            depth_distribution.append("   - Depth 3: 10-15 nodes (specific examples/applications)")
        if max_depth >= 4:
            depth_distribution.append("   - Depth 4: 12-18 nodes (detailed instances/processes)")
        if max_depth >= 5:
            depth_distribution.append("   - Depth 5: 15-20 nodes (fine-grained details/edge cases)")
        
        depth_guide = "\n".join(depth_distribution)
        
        # Build example nodes for each depth level
        example_nodes = []
        example_edges = []
        example_nodes.append('    {{"id": "1", "label": "Central Topic", "content": "Main concept", "depth": 0}}')
        
        for depth in range(1, max_depth + 1):
            node_id = depth + 1
            if depth == 1:
                label = f"Major Subtopic {depth}"
                content = "Key area description"
            elif depth == 2:
                label = f"Detailed Concept"
                content = "Specific detail"
            elif depth == 3:
                label = f"Specific Example"
                content = "Concrete instance"
            elif depth == 4:
                label = f"Detailed Process"
                content = "Step-by-step breakdown"
            else:  # depth 5
                label = f"Fine Detail"
                content = "Edge case or nuance"
            
            example_nodes.append(f'    {{"id": "{node_id}", "label": "{label}", "content": "{content}", "depth": {depth}}}')
            
            # Add edge from previous level
            if depth == 1:
                example_edges.append(f'    {{"from": "1", "to": "{node_id}", "label": "encompasses"}}')
            else:
                example_edges.append(f'    {{"from": "{node_id - 1}", "to": "{node_id}", "label": "consists of"}}')
        
        example_nodes_str = ",\n".join(example_nodes)
        example_edges_str = ",\n".join(example_edges)
        
        # Generate mind map structure with LLM
        prompt = f"""Based on the following content, create a comprehensive hierarchical mind map structure with EXACTLY {max_depth + 1} depth levels (0 through {max_depth}).

Content:
{context}

CRITICAL REQUIREMENTS - READ CAREFULLY:
1. Create EXACTLY {max_depth + 1} depth levels: depth {depth_levels}
2. Generate {total_nodes}-{total_nodes + 10} nodes total distributed across ALL {max_depth + 1} levels
3. Each node MUST have a unique numeric ID (as a string)
4. MANDATORY node distribution by depth:
{depth_guide}
5. Each edge MUST have a descriptive label explaining the relationship
   Examples: "is a type of", "causes", "leads to", "includes", "explains", "requires", "produces", "demonstrates", "applies to", "results in"
6. Keep node labels concise (2-5 words maximum)
7. Node content should be a brief description (1 sentence)

Return ONLY a valid JSON object with this EXACT structure:
{{
  "nodes": [
{example_nodes_str}
  ],
  "edges": [
{example_edges_str}
  ]
}}

ABSOLUTELY CRITICAL: 
- You MUST generate nodes for ALL depth levels from 0 to {max_depth}
- The maximum depth value in your nodes MUST be {max_depth}
- DO NOT stop at depth {max_depth - 2} or depth {max_depth - 1}
- Ensure depth {max_depth} has at least 12-20 nodes showing the finest level of detail
- Every depth level must have multiple nodes, not just one
- Double-check your JSON includes nodes with "depth": {max_depth} before returning"""

        logger.info(f"Generating mind map for notebook {notebook_id} with max_depth={max_depth}")
        
        # Call LLM with more tokens for larger structures and lower temperature for better instruction following
        response = llm_wrapper.llm.generate(prompt, max_tokens=4000, temperature=0.3, timeout=180)
        logger.info(f"LLM response length: {len(response)} chars")
        
        # Parse JSON response
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                mind_map_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
            
            nodes = mind_map_data.get('nodes', [])
            edges = mind_map_data.get('edges', [])
            
            # Validate depth levels were actually generated
            actual_depths = set(node.get('depth', 0) for node in nodes)
            max_node_depth = max(actual_depths) if actual_depths else 0
            
            if max_node_depth < max_depth:
                logger.warning(f"LLM only generated depth levels up to {max_node_depth}, expected {max_depth}")
                logger.warning(f"Depth levels present: {sorted(actual_depths)}")
                logger.warning(f"Missing depth levels: {set(range(max_depth + 1)) - actual_depths}")
            
            # Count nodes per depth level
            depth_counts = {}
            for node in nodes:
                depth = node.get('depth', 0)
                depth_counts[depth] = depth_counts.get(depth, 0) + 1
            
            logger.info(f"Node distribution by depth: {depth_counts}")
            
            # Calculate connections for each node
            for node in nodes:
                node_id = node['id']
                connections = sum(1 for edge in edges if edge['from'] == node_id or edge['to'] == node_id)
                node['connections'] = connections
            
            # Update mind map with generated data
            mindmap_crud.update_mind_map_data(
                db=db,
                mind_map_id=mind_map_id,
                nodes=nodes,
                edges=edges,
                node_count=len(nodes),
                depth=max_node_depth
            )
            
            logger.info(f"Generated mind map with {len(nodes)} nodes, {len(edges)} edges, max depth: {max_node_depth}/{max_depth}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response}")
            # Create a fallback simple structure
            fallback_nodes = [
                {"id": "1", "label": "Main Topic", "content": "Central concept", "depth": 0, "connections": 0}
            ]
            fallback_edges = []
            mindmap_crud.update_mind_map_data(
                db=db,
                mind_map_id=mind_map_id,
                nodes=fallback_nodes,
                edges=fallback_edges,
                node_count=1,
                depth=0
            )
            
    except Exception as e:
        logger.error(f"Failed to generate mind map data: {str(e)}")
        raise


@router.get("/mind-maps/{mind_map_id}/node-details/{node_id}")
async def get_node_details(
    mind_map_id: str,
    node_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed content for a specific node from the original document"""
    try:
        # Get mind map
        mind_map = mindmap_crud.get_mind_map(db, mind_map_id, user_id)
        if not mind_map:
            raise HTTPException(status_code=404, detail="Mind map not found")
        
        # Find the node
        node = None
        for n in mind_map.nodes:
            if n.get("id") == node_id:
                node = n
                break
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        # If no notebook linked, return just the node content
        if not mind_map.notebook_id:
            return {
                "node_id": node_id,
                "label": node.get("label", ""),
                "summary": node.get("content", ""),
                "details": [],
                "source": "generated"
            }
        
        # Query ChromaDB for detailed content (use same format as generation and notebooks)
        collection_name = f"clarity_user__{user_id.replace('|', '_')}__{mind_map.notebook_id}"
        
        logger.info(f"Querying collection: {collection_name} for node: {node.get('label')}")
        
        try:
            collection = chroma_service.client.get_collection(name=collection_name)
            
            # Create query embedding for the node label
            query_text = node.get("label", "") + " " + node.get("content", "")
            query_embedding = embedder.embed_query(query_text)
            
            # Query for relevant chunks
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5  # Get top 5 most relevant chunks
            )
            
            # Generate comprehensive summary using LLM
            comprehensive_summary = node.get("content", "")
            if results and results.get('documents') and results['documents'][0]:
                # Build context from top chunks
                context = "\n\n".join(results['documents'][0][:3])
                
                # Generate expanded summary
                prompt = f"""Explain {node.get('label', '')} based on this content. Write 3-4 clear sentences covering what it is, how it works, and why it matters. Use concrete examples where possible.

{context[:1500]}"""
                
                try:
                    summary_response = llm_wrapper.llm.generate(prompt, max_tokens=300)
                    if summary_response and len(summary_response.strip()) > 20:
                        comprehensive_summary = summary_response.strip()
                except Exception as llm_error:
                    logger.warning(f"Could not generate expanded summary: {llm_error}")
            
            # Format the details with concise excerpts
            details = []
            if results and results.get('documents'):
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    
                    # Extract most relevant sentence or create concise excerpt (max 200 chars)
                    content = doc.strip()
                    if len(content) > 200:
                        # Find a good breaking point (sentence or phrase)
                        sentences = content.split('. ')
                        excerpt = sentences[0]
                        if len(excerpt) > 200:
                            excerpt = content[:197] + "..."
                        else:
                            # Add more sentences if space allows
                            for sent in sentences[1:]:
                                if len(excerpt) + len(sent) + 2 <= 200:
                                    excerpt += ". " + sent
                                else:
                                    break
                            if not excerpt.endswith('.') and not excerpt.endswith('...'):
                                excerpt += "..."
                        content = excerpt
                    
                    details.append({
                        "content": content,
                        "source": metadata.get("source", "Unknown"),
                        "page": metadata.get("page"),
                        "relevance": 1.0 - (results['distances'][0][i] if results.get('distances') else 0)
                    })
            
            return {
                "node_id": node_id,
                "label": node.get("label", ""),
                "summary": comprehensive_summary,
                "details": details,
                "source": "document"
            }
            
        except Exception as chroma_error:
            logger.warning(f"Could not fetch from ChromaDB: {chroma_error}")
            return {
                "node_id": node_id,
                "label": node.get("label", ""),
                "summary": node.get("content", ""),
                "details": [],
                "source": "generated"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get node details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
