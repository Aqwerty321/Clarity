"""
FastAPI endpoints for local RAG backend
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header
from typing import Optional
import logging
import uuid

from ..models.schemas import (
    DocumentIngestResponse,
    EmbedRequest,
    EmbedResponse,
    AskRequest,
    AskResponse,
    SourceChunk,
    GenerateQuizRequest,
    GenerateQuizResponse,
    QuizQuestion,
    SyncPushRequest,
    SyncPushResponse,
    SyncPullResponse,
    HealthResponse
)
from ..services.embedder import embedder
from ..services.chroma_service import chroma_service
from ..services.llm_wrapper import llm_wrapper
from ..services.sync_client import sync_client
from ..utils.pdf_parser import extract_text_from_file
from ..utils.chunker import chunk_text

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    collections = chroma_service.list_collections()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        embedder_model=embedder.model_name,
        llm_model=llm_wrapper.get_model_name(),
        chroma_collections=len(collections)
    )


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    title: Optional[str] = Form(None)
):
    """
    Ingest a document: upload → parse → chunk → embed → store in ChromaDB
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename or "untitled"
        
        # Extract text
        logger.info(f"Extracting text from {filename}")
        text = extract_text_from_file(filename, content)
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        # Chunk text
        logger.info(f"Chunking text (length: {len(text)} chars)")
        chunks = chunk_text(text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks generated from document")
        
        # Prepare data for embedding
        chunk_texts = [chunk[0] for chunk in chunks]
        document_id = str(uuid.uuid4())
        doc_title = title or filename
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunk_texts)} chunks")
        embeddings = embedder.embed_texts(chunk_texts)
        
        # Prepare metadata
        metadatas = [
            {
                "document_id": document_id,
                "title": doc_title,
                "chunk_index": i,
                "char_start": chunk[1],
                "char_end": chunk[2]
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Store in ChromaDB
        logger.info(f"Storing {len(chunk_texts)} chunks in ChromaDB for user {user_id}")
        chroma_service.add_documents(
            user_id=user_id,
            documents=chunk_texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        return DocumentIngestResponse(
            document_id=document_id,
            title=doc_title,
            num_chunks=len(chunks),
            status="success",
            message=f"Ingested {len(chunks)} chunks"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/embed", response_model=EmbedResponse)
async def embed_texts(request: EmbedRequest):
    """Generate embeddings for texts (debugging endpoint)"""
    try:
        embeddings = embedder.embed_texts(request.texts)
        
        return EmbedResponse(
            embeddings=embeddings,
            model=embedder.model_name,
            dimension=embedder.dimension
        )
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    RAG question answering: embed query → retrieve chunks → generate answer
    """
    try:
        # Embed question
        notebook_info = f" in notebook {request.notebook_id}" if request.notebook_id else " across all notebooks"
        logger.info(f"Processing question from user {request.user_id}{notebook_info}: {request.question}")
        query_embedding = embedder.embed_query(request.question)
        
        # Determine collection name
        if request.notebook_id:
            # Query specific notebook collection
            collection_name = f"clarity_user__{request.user_id.replace('|', '_')}__{request.notebook_id}"
            try:
                collection = chroma_service.client.get_collection(name=collection_name)
                results_raw = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=request.top_k
                )
                # Convert to expected format
                results = {
                    "documents": results_raw["documents"][0] if results_raw["documents"] else [],
                    "distances": results_raw["distances"][0] if results_raw["distances"] else [],
                    "ids": results_raw["ids"][0] if results_raw["ids"] else [],
                    "metadatas": results_raw["metadatas"][0] if results_raw["metadatas"] else []
                }
            except Exception as e:
                logger.warning(f"Collection not found or error: {e}")
                results = {"documents": [], "distances": [], "ids": [], "metadatas": []}
        else:
            # Query all user documents (backward compatibility)
            results = chroma_service.query(
                user_id=request.user_id,
                query_embedding=query_embedding,
                top_k=request.top_k
            )
        
        if not results["documents"]:
            return AskResponse(
                answer="I don't have any relevant information to answer this question. Please upload some documents first.",
                source_chunks=[],
                model=llm_wrapper.get_model_name()
            )
        
        # Build source chunks
        source_chunks = [
            SourceChunk(
                id=results["ids"][i],
                text=results["documents"][i],
                score=1.0 - results["distances"][i],  # Convert distance to similarity
                metadata=results["metadatas"][i] if results["metadatas"] else None
            )
            for i in range(len(results["documents"]))
        ]
        
        # Generate answer using LLM
        context_texts = [chunk.text for chunk in source_chunks]
        answer = llm_wrapper.answer_question(
            question=request.question,
            context_chunks=context_texts
        )
        
        # Build prompt for transparency
        prompt = llm_wrapper.build_rag_prompt(
            question=request.question,
            context_chunks=context_texts,
            include_instructions=request.use_summary
        ) if request.use_summary else None
        
        return AskResponse(
            answer=answer,
            source_chunks=source_chunks,
            used_prompt=prompt,
            model=llm_wrapper.get_model_name()
        )
    
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest-quiz-topics")
async def suggest_quiz_topics(user_id: str):
    """Suggest quiz topics from user's documents"""
    try:
        # Get all documents for user
        results = chroma_service.query(
            user_id=user_id,
            query_embedding=[0.0] * embedder.get_embedding_dimension(),  # Dummy query to get all docs
            top_k=10
        )
        
        if not results["documents"]:
            return {"topics": []}
        
        # Use LLM to extract key topics from documents
        context = "\n\n".join(results["documents"][:5])
        prompt = f"""Based on the following content, suggest 5 quiz topics that would make good quiz subjects.

Content:
{context}

Output ONLY a JSON array of topic strings, like: ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"]"""
        
        response = llm_wrapper.llm.generate(prompt, max_tokens=200, temperature=0.7)
        
        # Parse topics
        import json
        import re
        json_match = re.search(r'\[.*\]', response)
        if json_match:
            topics = json.loads(json_match.group(0))
        else:
            topics = ["General knowledge from uploaded documents"]
        
        return {"topics": topics[:5]}
    
    except Exception as e:
        logger.error(f"Topic suggestion error: {e}", exc_info=True)
        return {"topics": ["General knowledge from uploaded documents"]}


@router.post("/generate-quiz", response_model=GenerateQuizResponse)
async def generate_quiz(request: GenerateQuizRequest):
    """Generate quiz questions from user's documents"""
    try:
        # Get relevant context for the topic
        notebook_info = f" from notebook {request.notebook_id}" if request.notebook_id else " from all notebooks"
        logger.info(f"Generating quiz for user {request.user_id}{notebook_info}, topic: {request.topic}")
        query_embedding = embedder.embed_query(request.topic)
        
        # Determine collection to query
        if request.notebook_id:
            # Query specific notebook collection
            collection_name = f"clarity_user__{request.user_id.replace('|', '_')}__{request.notebook_id}"
            try:
                collection = chroma_service.client.get_collection(name=collection_name)
                results_raw = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=5
                )
                # Convert to expected format
                results = {
                    "documents": results_raw["documents"][0] if results_raw["documents"] else [],
                    "distances": results_raw["distances"][0] if results_raw["distances"] else [],
                    "ids": results_raw["ids"][0] if results_raw["ids"] else [],
                    "metadatas": results_raw["metadatas"][0] if results_raw["metadatas"] else []
                }
            except Exception as e:
                logger.warning(f"Collection not found or error: {e}")
                results = {"documents": [], "distances": [], "ids": [], "metadatas": []}
        else:
            # Query all user documents (backward compatibility)
            results = chroma_service.query(
                user_id=request.user_id,
                query_embedding=query_embedding,
                top_k=5
            )
        
        if not results["documents"]:
            raise HTTPException(
                status_code=404,
                detail="No documents found for this topic"
            )
        
        # Generate quiz
        logger.info(f"Generating quiz for topic: {request.topic}")
        quiz_text = llm_wrapper.generate_quiz(
            topic=request.topic,
            context_chunks=results["documents"],
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        
        logger.info(f"LLM returned quiz text (length: {len(quiz_text)} chars)")
        
        # Parse JSON response
        import json
        import re
        
        # Try to extract JSON from response (in case LLM adds markdown)
        json_match = re.search(r'\{[\s\S]*\}', quiz_text)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = quiz_text
        
        try:
            quiz_data = json.loads(json_str)
            questions = []
            
            for q_data in quiz_data.get("questions", []):
                questions.append(
                    QuizQuestion(
                        question=q_data["question"],
                        options=q_data["options"][:4],
                        correct_answer=q_data.get("correct_answer", 0),
                        explanation=q_data.get("explanation", "Generated from your documents."),
                        hint=q_data.get("hint"),
                        incorrect_explanations=q_data.get("incorrect_explanations")
                    )
                )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON. Error: {e}")
            logger.error(f"Quiz text was:\n{quiz_text}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse quiz JSON: {str(e)}"
            )
        
        # If parsing failed, log the quiz text and return error
        if not questions:
            logger.error(f"Failed to parse quiz. Quiz text was:\n{quiz_text}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse quiz questions from LLM output. Generated {len(quiz_text)} chars but no questions parsed."
            )
        
        logger.info(f"Successfully parsed {len(questions)} questions")
        return GenerateQuizResponse(
            title=f"Quiz: {request.topic}",
            questions=questions,
            topic=request.topic,
            difficulty=request.difficulty
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/push", response_model=SyncPushResponse)
async def sync_push(
    request: SyncPushRequest,
    authorization: Optional[str] = Header(None)
):
    """Push local notebook state to cloud"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        access_token = authorization.split(" ")[1]
        
        # Call Render backend
        result = await sync_client.push_notebooks(
            user_id=request.user_id,
            notebooks=request.notebooks,
            access_token=access_token,
            last_sync=request.last_sync
        )
        
        return SyncPushResponse(
            status=result.get("status", "success"),
            synced_count=result.get("synced_count", len(request.notebooks)),
            conflicts=result.get("conflicts", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync push error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/pull", response_model=SyncPullResponse)
async def sync_pull(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """Pull cloud notebook state to local"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        access_token = authorization.split(" ")[1]
        
        # Call Render backend
        result = await sync_client.pull_notebooks(
            user_id=user_id,
            access_token=access_token
        )
        
        return SyncPullResponse(
            notebooks=result.get("notebooks", []),
            last_sync=result.get("last_sync")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync pull error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Quiz Endpoints
# ============================================================================

@router.post("/quizzes")
async def create_quiz(
    user_id: str = Form(...),
    notebook_id: Optional[str] = Form(None),
    title: str = Form(...),
    topic: Optional[str] = Form(None),
    difficulty: Optional[str] = Form(None),
    questions: str = Form(...)  # JSON string
):
    """Save a quiz"""
    try:
        from ..db import get_db, quiz_crud
        import json
        
        db = next(get_db())
        
        # Parse questions JSON
        questions_data = json.loads(questions)
        
        quiz = quiz_crud.create_quiz(
            db=db,
            user_id=user_id,
            notebook_id=notebook_id,
            title=title,
            topic=topic,
            difficulty=difficulty,
            questions=questions_data
        )
        
        return quiz.to_dict()
    
    except Exception as e:
        logger.error(f"Failed to create quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quizzes")
async def get_quizzes(user_id: str, notebook_id: Optional[str] = None):
    """Get all quizzes for a user, optionally filtered by notebook"""
    try:
        from ..db import get_db, quiz_crud
        
        db = next(get_db())
        
        if notebook_id:
            quizzes = quiz_crud.get_quizzes_by_notebook(db, notebook_id, user_id)
        else:
            quizzes = quiz_crud.get_quizzes_by_user(db, user_id)
        
        return [quiz.to_dict() for quiz in quizzes]
    
    except Exception as e:
        logger.error(f"Failed to get quizzes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str, user_id: str):
    """Get a specific quiz"""
    try:
        from ..db import get_db, quiz_crud
        
        db = next(get_db())
        quiz = quiz_crud.get_quiz(db, quiz_id, user_id)
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return quiz.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str, user_id: str):
    """Delete a quiz"""
    try:
        from ..db import get_db, quiz_crud
        
        db = next(get_db())
        success = quiz_crud.delete_quiz(db, quiz_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return {"message": "Quiz deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Analytics Endpoints ====================

@router.post("/quiz-attempts")
async def record_quiz_attempt(
    user_id: str = Form(...),
    quiz_id: str = Form(...),
    notebook_id: str = Form(None),
    topic: str = Form(...),
    difficulty: str = Form(...),
    answers: str = Form(...),  # JSON string
    score: float = Form(...),
    correct_count: int = Form(...),
    total_questions: int = Form(...)
):
    """Record a quiz attempt for analytics"""
    try:
        from ..db import get_db, analytics_crud, gamification_crud
        import json
        
        db = next(get_db())
        answers_data = json.loads(answers)
        
        # Normalize topic using AI (in background, use original for now)
        normalized_topic = await normalize_topic(user_id, topic)
        
        attempt = analytics_crud.create_quiz_attempt(
            db, user_id, quiz_id, notebook_id, topic, difficulty,
            answers_data, score, correct_count, total_questions, normalized_topic
        )
        
        # Update user's streak and award points (pass difficulty for point calculation)
        streak_result = gamification_crud.update_user_activity(db, user_id, difficulty)
        
        return {
            **attempt.to_dict(),
            "streak": streak_result["streak"],
            "pointsEarned": streak_result["pointsEarned"],
            "milestone": streak_result["milestone"]
        }
    
    except Exception as e:
        logger.error(f"Failed to record quiz attempt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flashcard-attempts")
async def record_flashcard_attempt(
    user_id: str = Form(...),
    deck_id: str = Form(...),
    card_id: str = Form(...),
    notebook_id: str = Form(None),
    topic: str = Form(...),
    quality: int = Form(...),
    was_correct: bool = Form(...)
):
    """Record a flashcard attempt for analytics"""
    try:
        from ..db import get_db, analytics_crud
        
        db = next(get_db())
        
        # Normalize topic using AI
        normalized_topic = await normalize_topic(user_id, topic)
        
        attempt = analytics_crud.create_flashcard_attempt(
            db, user_id, deck_id, card_id, notebook_id, topic,
            quality, was_correct, normalized_topic
        )
        
        return attempt.to_dict()
    
    except Exception as e:
        logger.error(f"Failed to record flashcard attempt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/overview")
async def get_analytics_overview(user_id: str, notebook_id: Optional[str] = None):
    """Get comprehensive analytics data for dashboards"""
    try:
        from ..db import get_db, analytics_crud
        from collections import defaultdict
        
        db = next(get_db())
        
        # Fetch all attempts
        quiz_attempts = analytics_crud.get_quiz_attempts_by_user(db, user_id, notebook_id)
        flashcard_attempts = analytics_crud.get_flashcard_attempts_by_user(db, user_id, notebook_id)
        
        # Topic coverage analysis
        topic_stats = defaultdict(lambda: {
            'quiz_count': 0,
            'flashcard_count': 0,
            'total_questions': 0,
            'correct_answers': 0
        })
        
        for attempt in quiz_attempts:
            topic = attempt.normalized_topic
            topic_stats[topic]['quiz_count'] += 1
            topic_stats[topic]['total_questions'] += attempt.total_questions
            topic_stats[topic]['correct_answers'] += attempt.correct_count
        
        for attempt in flashcard_attempts:
            topic = attempt.normalized_topic
            topic_stats[topic]['flashcard_count'] += 1
            if attempt.was_correct:
                topic_stats[topic]['correct_answers'] += 1
            topic_stats[topic]['total_questions'] += 1
        
        # Difficulty distribution
        difficulty_stats = defaultdict(lambda: {'correct': 0, 'incorrect': 0})
        for attempt in quiz_attempts:
            diff = attempt.difficulty or 'medium'
            difficulty_stats[diff]['correct'] += attempt.correct_count
            difficulty_stats[diff]['incorrect'] += (attempt.total_questions - attempt.correct_count)
        
        # Overall accuracy
        total_correct = sum(a.correct_count for a in quiz_attempts) + \
                       sum(1 for a in flashcard_attempts if a.was_correct)
        total_questions = sum(a.total_questions for a in quiz_attempts) + len(flashcard_attempts)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'topic_coverage': dict(topic_stats),
            'difficulty_distribution': dict(difficulty_stats),
            'overall_accuracy': round(overall_accuracy, 1),
            'total_quizzes': len(quiz_attempts),
            'total_flashcard_reviews': len(flashcard_attempts),
            'total_questions_answered': total_questions,
            'total_correct_answers': total_correct
        }
    
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quiz-attempts/latest/{quiz_id}")
async def get_latest_quiz_attempt(quiz_id: str, user_id: str):
    """Get the most recent attempt for a specific quiz"""
    try:
        from ..db import get_db
        from ..db.analytics_models import QuizAttempt
        
        db = next(get_db())
        
        attempt = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.user_id == user_id
        ).order_by(QuizAttempt.attempted_at.desc()).first()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="No attempts found for this quiz")
        
        return attempt.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest quiz attempt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def normalize_topic(user_id: str, topic: str) -> str:
    """Normalize topic name using AI (cached)"""
    try:
        from ..db import get_db, analytics_crud
        
        db = next(get_db())
        
        # Check cache first
        mappings = analytics_crud.get_topic_mappings(db, user_id)
        for mapping in mappings:
            if mapping.original_topic.lower() == topic.lower():
                return mapping.normalized_topic
        
        # Use AI to normalize
        prompt = f"""Given the topic: "{topic}"

Normalize this topic to a standard form. Topics about the same subject should have the same normalized name.
For example:
- "chem reactions" -> "Chemical Reactions"
- "chemical reactions" -> "Chemical Reactions"
- "ML basics" -> "Machine Learning Basics"
- "machine learning fundamentals" -> "Machine Learning Basics"

Return ONLY the normalized topic name, nothing else."""

        normalized = llm_wrapper.generate_text(prompt).strip()
        
        # Cache the mapping
        analytics_crud.get_or_create_topic_mapping(db, user_id, topic, normalized)
        
        return normalized
    
    except Exception as e:
        logger.error(f"Failed to normalize topic: {e}")
        return topic  # Fallback to original


# ==========================================
# Conversation History Endpoints
# ==========================================

@router.post("/conversations")
async def save_conversation(
    notebook_id: str = Form(...),
    question: str = Form(...),
    answer: str = Form(...),
    sources: Optional[str] = Form(None),
    used_summary: bool = Form(False),
    user_id: str = Header(..., alias="X-User-Id")
):
    """Save a notebook conversation"""
    try:
        from ..db import get_db, conversation_crud
        import json
        
        db = next(get_db())
        
        # Parse sources if provided
        sources_list = json.loads(sources) if sources else None
        
        conversation = conversation_crud.create_conversation(
            db=db,
            notebook_id=notebook_id,
            user_id=user_id,
            question=question,
            answer=answer,
            sources=sources_list,
            used_summary=used_summary
        )
        
        return {
            "success": True,
            "conversation": conversation.to_dict()
        }
    except Exception as e:
        logger.error(f"Failed to save conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{notebook_id}")
async def get_conversations(
    notebook_id: str,
    limit: int = 50,
    user_id: str = Header(..., alias="X-User-Id")
):
    """Get all conversations for a notebook"""
    try:
        from ..db import get_db, conversation_crud
        
        db = next(get_db())
        
        conversations = conversation_crud.get_conversations_by_notebook(
            db=db,
            notebook_id=notebook_id,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "success": True,
            "conversations": [conv.to_dict() for conv in conversations]
        }
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Header(..., alias="X-User-Id")
):
    """Delete a conversation"""
    try:
        from ..db import get_db, conversation_crud
        
        db = next(get_db())
        
        success = conversation_crud.delete_conversation(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/notebook/{notebook_id}")
async def clear_notebook_conversations(
    notebook_id: str,
    user_id: str = Header(..., alias="X-User-Id")
):
    """Clear all conversations for a notebook"""
    try:
        from ..db import get_db, conversation_crud
        
        db = next(get_db())
        
        count = conversation_crud.clear_notebook_conversations(
            db=db,
            notebook_id=notebook_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "deleted_count": count
        }
    except Exception as e:
        logger.error(f"Failed to clear conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
