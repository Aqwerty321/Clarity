"""API endpoints for gamification features"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/streak/{user_id}")
async def get_user_streak(user_id: str):
    """Get user's streak and points information"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        streak = gamification_crud.get_or_create_user_streak(db, user_id)
        
        return streak.to_dict()
    
    except Exception as e:
        logger.error(f"Failed to get user streak: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/streak/{user_id}/update")
async def update_streak(user_id: str):
    """Update streak when user completes a quiz"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        result = gamification_crud.update_user_activity(db, user_id)
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to update streak: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace")
async def get_marketplace(
    category: Optional[str] = None,
    rarity: Optional[str] = None,
    featured: bool = False
):
    """Get marketplace items with optional filters"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        items = gamification_crud.get_marketplace_items(db, category, rarity, featured)
        
        return [item.to_dict() for item in items]
    
    except Exception as e:
        logger.error(f"Failed to get marketplace items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/{item_id}")
async def get_item(item_id: str):
    """Get a single marketplace item"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        item = gamification_crud.get_marketplace_item(db, item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return item.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get marketplace item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketplace/purchase")
async def purchase_item(user_id: str, item_id: str):
    """Purchase a marketplace item"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        result = gamification_crud.purchase_item(db, user_id, item_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to purchase item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchases/{user_id}")
async def get_purchases(user_id: str):
    """Get user's purchase history"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        purchases = gamification_crud.get_user_purchases(db, user_id)
        
        return [p.to_dict() for p in purchases]
    
    except Exception as e:
        logger.error(f"Failed to get purchases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchases/{user_id}/owns/{item_id}")
async def check_ownership(user_id: str, item_id: str):
    """Check if user owns an item"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        owns = gamification_crud.has_purchased(db, user_id, item_id)
        
        return {"owns": owns}
    
    except Exception as e:
        logger.error(f"Failed to check ownership: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketplace/seed")
async def seed_marketplace():
    """Seed marketplace with demo data (development only)"""
    try:
        from ..db import get_db, gamification_crud
        
        db = next(get_db())
        gamification_crud.seed_marketplace_items(db)
        
        return {"message": "Marketplace seeded successfully"}
    
    except Exception as e:
        logger.error(f"Failed to seed marketplace: {e}")
        raise HTTPException(status_code=500, detail=str(e))
