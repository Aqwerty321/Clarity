"""CRUD operations for gamification features"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from .gamification_models import UserStreak, MarketplaceItem, UserPurchase


def get_or_create_user_streak(db: Session, user_id: str) -> UserStreak:
    """Get or create user streak record"""
    streak = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
    if not streak:
        streak = UserStreak(user_id=user_id)
        db.add(streak)
        db.commit()
        db.refresh(streak)
    return streak


def update_user_activity(db: Session, user_id: str, difficulty: str = 'medium') -> dict:
    """Update user's streak when they complete a quiz"""
    streak = get_or_create_user_streak(db, user_id)
    points_earned = streak.update_streak(difficulty=difficulty)
    db.commit()
    db.refresh(streak)
    
    return {
        "streak": streak.to_dict(),
        "pointsEarned": points_earned,
        "milestone": get_milestone_message(streak.current_streak)
    }


def get_milestone_message(streak_days: int) -> Optional[str]:
    """Get congratulatory message for streak milestones"""
    milestones = {
        3: "🔥 3-day streak! You're on fire!",
        7: "⭐ Week warrior! 7 days strong!",
        14: "💪 Two weeks! Unstoppable!",
        30: "🏆 Monthly master! 30 days!",
        60: "🚀 60-day legend!",
        100: "👑 Century streak! You're a champion!",
        365: "🌟 ONE YEAR STREAK! Absolutely legendary!"
    }
    return milestones.get(streak_days)


def get_marketplace_items(
    db: Session, 
    category: Optional[str] = None,
    rarity: Optional[str] = None,
    featured_only: bool = False
) -> List[MarketplaceItem]:
    """Get marketplace items with optional filters"""
    query = db.query(MarketplaceItem)
    
    if category:
        query = query.filter(MarketplaceItem.category == category)
    if rarity:
        query = query.filter(MarketplaceItem.rarity == rarity)
    if featured_only:
        query = query.filter(MarketplaceItem.is_featured == True)
    
    return query.order_by(MarketplaceItem.is_featured.desc(), MarketplaceItem.created_at.desc()).all()


def get_marketplace_item(db: Session, item_id: str) -> Optional[MarketplaceItem]:
    """Get a single marketplace item"""
    return db.query(MarketplaceItem).filter(MarketplaceItem.id == item_id).first()


def purchase_item(db: Session, user_id: str, item_id: str) -> dict:
    """Purchase a marketplace item"""
    # Get user streak (points wallet)
    streak = get_or_create_user_streak(db, user_id)
    
    # Get item
    item = get_marketplace_item(db, item_id)
    if not item:
        return {"success": False, "error": "Item not found"}
    
    # Check if already purchased
    existing = db.query(UserPurchase).filter(
        UserPurchase.user_id == user_id,
        UserPurchase.item_id == item_id
    ).first()
    if existing:
        return {"success": False, "error": "Already purchased"}
    
    # Check if enough points
    if not streak.spend_points(item.price):
        return {"success": False, "error": "Insufficient points"}
    
    # Create purchase
    purchase = UserPurchase(
        id=str(uuid.uuid4()),
        user_id=user_id,
        item_id=item_id,
        item_title=item.title,
        item_category=item.category,
        price_paid=item.price
    )
    
    db.add(purchase)
    db.commit()
    db.refresh(streak)
    
    return {
        "success": True,
        "purchase": purchase.to_dict(),
        "remainingPoints": streak.available_points
    }


def get_user_purchases(db: Session, user_id: str) -> List[UserPurchase]:
    """Get all purchases by a user"""
    return db.query(UserPurchase).filter(
        UserPurchase.user_id == user_id
    ).order_by(UserPurchase.purchased_at.desc()).all()


def has_purchased(db: Session, user_id: str, item_id: str) -> bool:
    """Check if user has purchased an item"""
    return db.query(UserPurchase).filter(
        UserPurchase.user_id == user_id,
        UserPurchase.item_id == item_id
    ).first() is not None


def purchase_streak_freeze(db: Session, user_id: str, days: int = 3) -> dict:
    """Purchase a streak freeze (powerup)"""
    freeze_cost = 200 * days  # 200 points per day (doubled)
    
    streak = get_or_create_user_streak(db, user_id)
    
    if not streak.spend_points(freeze_cost):
        return {"success": False, "error": "Insufficient points"}
    
    from datetime import timedelta
    streak.streak_frozen = True
    streak.freeze_expires = datetime.utcnow() + timedelta(days=days)
    
    db.commit()
    db.refresh(streak)
    
    return {
        "success": True,
        "message": f"Streak freeze activated for {days} days!",
        "freezeExpires": streak.freeze_expires.isoformat(),
        "remainingPoints": streak.available_points
    }


def seed_marketplace_items(db: Session):
    """Seed the marketplace with demo scholarly content"""
    demo_items = [
        # Research Papers - Legendary
        {
            "id": "paper-1",
            "title": "Quantum Entanglement and Information Theory: A Comprehensive Review",
            "description": "Groundbreaking research on quantum mechanics and its implications for information science. This seminal paper explores the fundamental principles of quantum entanglement and their applications in quantum computing and cryptography.",
            "category": "research_paper",
            "author": "Dr. Sarah Chen, MIT",
            "source": "Nature Physics",
            "year": 2024,
            "price": 1000,
            "rarity": "legendary",
            "tags": '["quantum physics", "information theory", "computing"]',
            "preview_text": "Recent advances in quantum computing have brought renewed attention to the phenomenon of quantum entanglement...",
            "is_featured": True
        },
        {
            "id": "paper-2",
            "title": "CRISPR-Cas9: Next Generation Gene Editing Techniques",
            "description": "Cutting-edge research on gene editing technology and its therapeutic applications. Includes case studies and ethical considerations.",
            "category": "research_paper",
            "author": "Prof. James Anderson, Stanford",
            "source": "Cell Biology Review",
            "year": 2024,
            "price": 900,
            "rarity": "legendary",
            "tags": '["biology", "genetics", "CRISPR", "medicine"]',
            "preview_text": "The development of CRISPR-Cas9 has revolutionized molecular biology...",
            "is_featured": True
        },
        
        # Research Papers - Epic
        {
            "id": "paper-3",
            "title": "Machine Learning in Drug Discovery: A Meta-Analysis",
            "description": "Comprehensive analysis of ML applications in pharmaceutical research. Covers neural networks, prediction models, and success rates.",
            "category": "research_paper",
            "author": "Dr. Maria Rodriguez, Harvard",
            "source": "Journal of Computational Chemistry",
            "year": 2023,
            "price": 700,
            "rarity": "epic",
            "tags": '["AI", "machine learning", "pharmaceuticals", "chemistry"]',
            "preview_text": "Artificial intelligence is transforming drug discovery pipelines...",
            "is_featured": False
        },
        {
            "id": "paper-4",
            "title": "Neuroplasticity and Learning: fMRI Studies",
            "description": "Functional MRI studies revealing how the brain reorganizes during learning. Essential reading for neuroscience students.",
            "category": "research_paper",
            "author": "Dr. Robert Kim, Johns Hopkins",
            "source": "Neuroscience Today",
            "year": 2023,
            "price": 600,
            "rarity": "epic",
            "tags": '["neuroscience", "fMRI", "learning", "brain"]',
            "preview_text": "The brain's remarkable ability to reorganize itself...",
            "is_featured": True
        },
        
        # Research Papers - Rare
        {
            "id": "paper-5",
            "title": "Climate Models and Prediction Accuracy: 2024 Assessment",
            "description": "Latest climate modeling techniques and their accuracy in predicting global temperature changes.",
            "category": "research_paper",
            "author": "Dr. Emily Watson, Oxford",
            "source": "Environmental Science Quarterly",
            "year": 2024,
            "price": 500,
            "rarity": "rare",
            "tags": '["climate", "modeling", "environment"]',
            "preview_text": "As climate change accelerates, accurate prediction models become crucial...",
            "is_featured": False
        },
        {
            "id": "paper-6",
            "title": "Blockchain Beyond Cryptocurrency: Enterprise Applications",
            "description": "Exploring blockchain technology in supply chain, healthcare, and finance sectors.",
            "category": "research_paper",
            "author": "Prof. David Lee, Carnegie Mellon",
            "source": "IEEE Blockchain Journal",
            "year": 2023,
            "price": 400,
            "rarity": "rare",
            "tags": '["blockchain", "technology", "enterprise"]',
            "preview_text": "Blockchain technology has evolved far beyond its cryptocurrency origins...",
            "is_featured": False
        },
        
        # Study Guides - Epic
        {
            "id": "guide-1",
            "title": "Organic Chemistry Mastery: Complete Reaction Mechanisms",
            "description": "Comprehensive guide to all major organic chemistry reactions with detailed mechanisms, practice problems, and mnemonic devices.",
            "category": "study_guide",
            "author": "Dr. Michael Zhang",
            "source": "Chemistry Excellence Series",
            "year": 2024,
            "price": 560,
            "rarity": "epic",
            "tags": '["chemistry", "organic chemistry", "study guide"]',
            "preview_text": "Master every reaction mechanism with step-by-step explanations...",
            "is_featured": True
        },
        {
            "id": "guide-2",
            "title": "Advanced Calculus Problem Set: 1000+ Solutions",
            "description": "Curated collection of challenging calculus problems with detailed solutions. Perfect for exam preparation.",
            "category": "study_guide",
            "author": "Prof. Lisa Thompson",
            "source": "Mathematics Mastery",
            "year": 2024,
            "price": 500,
            "rarity": "epic",
            "tags": '["mathematics", "calculus", "problem solving"]',
            "preview_text": "From limits to multivariate integration, conquer calculus...",
            "is_featured": False
        },
        
        # Study Guides - Rare
        {
            "id": "guide-3",
            "title": "Psychology: Memory Techniques for Academic Success",
            "description": "Evidence-based memory techniques and study strategies backed by cognitive psychology research.",
            "category": "study_guide",
            "author": "Dr. Amanda Foster",
            "source": "Learning Sciences Institute",
            "year": 2023,
            "price": 360,
            "rarity": "rare",
            "tags": '["psychology", "memory", "study skills"]',
            "preview_text": "Learn how your brain encodes information and optimize your study sessions...",
            "is_featured": False
        },
        
        # Tools - Rare
        {
            "id": "tool-1",
            "title": "Academic Citation Manager Pro",
            "description": "Advanced tool for managing citations across APA, MLA, Chicago styles. Auto-generate bibliographies.",
            "category": "tool",
            "author": "Clarity Team",
            "source": "Clarity Tools",
            "year": 2024,
            "price": 300,
            "rarity": "rare",
            "tags": '["productivity", "citations", "research"]',
            "preview_text": "Never worry about citation formatting again...",
            "is_featured": False
        },
        {
            "id": "tool-2",
            "title": "LaTeX Math Formula Library",
            "description": "Comprehensive LaTeX templates and formulas for mathematics, physics, and engineering papers.",
            "category": "tool",
            "author": "Clarity Team",
            "source": "Clarity Tools",
            "year": 2024,
            "price": 240,
            "rarity": "rare",
            "tags": '["LaTeX", "mathematics", "formatting"]',
            "preview_text": "Beautiful mathematical typesetting made easy...",
            "is_featured": False
        },
        
        # Powerups - Common
        {
            "id": "powerup-1",
            "title": "3-Day Streak Freeze",
            "description": "Protect your streak! This freeze prevents your streak from breaking if you miss a day. Valid for 3 days.",
            "category": "powerup",
            "author": "Clarity",
            "source": "Powerups",
            "year": 2024,
            "price": 600,
            "rarity": "common",
            "tags": '["streak", "powerup", "protection"]',
            "preview_text": "Life happens! Don't lose your hard-earned streak.",
            "is_featured": True
        },
        {
            "id": "powerup-2",
            "title": "7-Day Streak Freeze",
            "description": "Ultimate protection for your streak! Valid for 7 days. Perfect for vacations or busy weeks.",
            "category": "powerup",
            "author": "Clarity",
            "source": "Powerups",
            "year": 2024,
            "price": 1400,
            "rarity": "rare",
            "tags": '["streak", "powerup", "protection"]',
            "preview_text": "Extended protection for ultimate peace of mind.",
            "is_featured": False
        }
    ]
    
    for item_data in demo_items:
        existing = db.query(MarketplaceItem).filter(MarketplaceItem.id == item_data["id"]).first()
        if not existing:
            item = MarketplaceItem(**item_data)
            db.add(item)
        else:
            # Update existing item with new price
            for key, value in item_data.items():
                setattr(existing, key, value)
    
    db.commit()
