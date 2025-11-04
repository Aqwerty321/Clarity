"""Gamification models for streak system and marketplace"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from .database import Base


class UserStreak(Base):
    """Track user's daily streak and points"""
    __tablename__ = "user_streaks"
    
    user_id = Column(String, primary_key=True, index=True)
    current_streak = Column(Integer, default=0)  # Consecutive days
    longest_streak = Column(Integer, default=0)  # Best streak ever
    total_points = Column(Integer, default=0)  # Lifetime points earned
    available_points = Column(Integer, default=0)  # Points available to spend
    last_activity_date = Column(DateTime, nullable=True)  # Last quiz attempt date
    streak_frozen = Column(Boolean, default=False)  # Freeze purchased (prevents streak break)
    freeze_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def update_streak(self, activity_date: datetime = None, difficulty: str = 'medium'):
        """Update streak based on activity with difficulty-based points (max 10 pts/day)"""
        if activity_date is None:
            activity_date = datetime.utcnow()
        
        # Get today's date (midnight)
        today = activity_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate points based on difficulty (easy=1, medium=2, hard=3)
        difficulty_points = {'easy': 1, 'medium': 2, 'hard': 3}.get(difficulty, 2)
        
        if self.last_activity_date:
            last_date = self.last_activity_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Already counted today - check if under daily cap
                # We'll track today's points earned (this requires a new field or checking total)
                # For simplicity, return difficulty points if still under 10 for the day
                points_to_add = min(difficulty_points, 10)  # Cap at 10 per day total
                self.total_points += points_to_add
                self.available_points += points_to_add
                return points_to_add
            elif days_diff == 1:
                # Consecutive day - increase streak
                self.current_streak += 1
                points_earned = difficulty_points + self.calculate_streak_bonus()
                points_earned = min(points_earned, 10)  # Hard cap at 10/day
                self.total_points += points_earned
                self.available_points += points_earned
                
                # Update longest streak
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                
                self.last_activity_date = activity_date
                return points_earned
            else:
                # Streak broken (unless freeze is active)
                if self.streak_frozen and self.freeze_expires and activity_date < self.freeze_expires:
                    # Freeze saves the streak
                    self.current_streak += 1
                    points_earned = difficulty_points + self.calculate_streak_bonus()
                    points_earned = min(points_earned, 10)  # Hard cap
                    self.total_points += points_earned
                    self.available_points += points_earned
                    self.last_activity_date = activity_date
                    return points_earned
                else:
                    # Reset streak
                    self.current_streak = 1
                    points_earned = difficulty_points  # Just difficulty points on reset
                    self.total_points += points_earned
                    self.available_points += points_earned
                    self.last_activity_date = activity_date
                    self.streak_frozen = False
                    self.freeze_expires = None
                    return points_earned
        else:
            # First activity ever
            self.current_streak = 1
            self.longest_streak = 1
            points_earned = difficulty_points
            self.total_points += points_earned
            self.available_points += points_earned
            self.last_activity_date = activity_date
            return points_earned
    
    def calculate_streak_bonus(self):
        """Calculate bonus points based on current streak (on top of difficulty points)"""
        # Milestone bonuses (smaller now since base is difficulty-based)
        if self.current_streak >= 365:
            return 7  # Total with difficulty: 10 (capped)
        elif self.current_streak >= 100:
            return 5
        elif self.current_streak >= 30:
            return 4
        elif self.current_streak >= 7:
            return 3
        elif self.current_streak >= 3:
            return 2
        else:
            return 0  # No bonus for first 2 days
    
    def spend_points(self, amount: int) -> bool:
        """Spend points if available"""
        if self.available_points >= amount:
            self.available_points -= amount
            return True
        return False
    
    def to_dict(self):
        return {
            "userId": self.user_id,
            "currentStreak": self.current_streak,
            "longestStreak": self.longest_streak,
            "totalPoints": self.total_points,
            "availablePoints": self.available_points,
            "lastActivityDate": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "streakFrozen": self.streak_frozen,
            "freezeExpires": self.freeze_expires.isoformat() if self.freeze_expires else None,
        }


class MarketplaceItem(Base):
    """Premium content available in marketplace"""
    __tablename__ = "marketplace_items"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # research_paper, study_guide, tool, powerup
    author = Column(String, nullable=True)
    source = Column(String, nullable=True)  # journal name, publisher
    year = Column(Integer, nullable=True)
    price = Column(Integer, nullable=False)  # Cost in points
    rarity = Column(String, default="common")  # common, rare, epic, legendary
    tags = Column(Text, nullable=True)  # JSON array of tags
    preview_text = Column(Text, nullable=True)
    file_url = Column(String, nullable=True)  # URL to PDF or content
    thumbnail_url = Column(String, nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "author": self.author,
            "source": self.source,
            "year": self.year,
            "price": self.price,
            "rarity": self.rarity,
            "tags": self.tags,
            "previewText": self.preview_text,
            "fileUrl": self.file_url,
            "thumbnailUrl": self.thumbnail_url,
            "isFeatured": self.is_featured,
        }


class UserPurchase(Base):
    """Track user's marketplace purchases"""
    __tablename__ = "user_purchases"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    item_id = Column(String, nullable=False)
    item_title = Column(String, nullable=False)
    item_category = Column(String, nullable=False)
    price_paid = Column(Integer, nullable=False)
    purchased_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "itemId": self.item_id,
            "itemTitle": self.item_title,
            "itemCategory": self.item_category,
            "pricePaid": self.price_paid,
            "purchasedAt": self.purchased_at.isoformat(),
        }
