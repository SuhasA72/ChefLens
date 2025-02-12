"""
Database management module for recipe storage and retrieval.
Implements a SQLite-based storage solution with pandas DataFrame interface.
"""

import pandas as pd
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class DatabaseConfig:
    """Configuration for database paths and settings."""
    base_dir: str
    data_dir: str
    recipes_file: str
    feedback_file: str
    leaderboard_file: str

class RecipeDatabase:
    """Manages all database operations for recipes, feedback, and leaderboard."""

    def __init__(self):
        self.config = self._initialize_config()
        self._ensure_directories()
        self._initialize_database()
        
    def _initialize_config(self) -> DatabaseConfig:
        """Initialize database configuration."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        
        return DatabaseConfig(
            base_dir=base_dir,
            data_dir=data_dir,
            recipes_file=os.path.join(data_dir, 'recipes.csv'),
            feedback_file=os.path.join(data_dir, 'feedback.csv'),
            leaderboard_file=os.path.join(data_dir, 'leaderboard.csv')
        )

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        os.makedirs(self.config.data_dir, exist_ok=True)
        logger.info(f"Data directory ensured at: {self.config.data_dir}")

    def _initialize_database(self) -> None:
        """Initialize database files with proper schema."""
        # Initialize recipes database
        if not os.path.exists(self.config.recipes_file):
            self._create_recipes_table()
            
        # Initialize feedback database
        if not os.path.exists(self.config.feedback_file):
            self._create_feedback_table()
            
        # Initialize leaderboard
        if not os.path.exists(self.config.leaderboard_file):
            self._create_leaderboard_table()

    def _create_recipes_table(self) -> None:
        """Create recipes table with initial schema."""
        pd.DataFrame({
            'title': [],
            'url': [],
            'recipe_text': [],
            'likes': pd.Series(dtype='int64'),
            'date_added': []
        }).to_csv(self.config.recipes_file, index=False)
        logger.info(f"Created recipes database at: {self.config.recipes_file}")

    def _create_feedback_table(self) -> None:
        """Create feedback table with initial schema."""
        pd.DataFrame(columns=[
            'recipe_title', 'feedback', 'sentiment', 'date_added'
        ]).to_csv(self.config.feedback_file, index=False)
        logger.info(f"Created feedback database at: {self.config.feedback_file}")

    def _create_leaderboard_table(self) -> None:
        """Create leaderboard table with initial schema."""
        pd.DataFrame(columns=[
            'user_name', 'recipes_tried', 'feedback_given', 'points'
        ]).to_csv(self.config.leaderboard_file, index=False)
        logger.info(f"Created leaderboard database at: {self.config.leaderboard_file}")

    def save_recipe(self, title: str, url: str, recipe_text: str) -> bool:
        """
        Save a new recipe to the database.
        
        Args:
            title (str): Recipe title
            url (str): Source URL
            recipe_text (str): Full recipe content
            
        Returns:
            bool: Success status
        """
        try:
            df = pd.read_csv(self.config.recipes_file)
            if df[df['title'] == title].empty:
                new_recipe = pd.DataFrame([{
                    'title': title,
                    'url': url,
                    'recipe_text': recipe_text,
                    'likes': 0,
                    'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }])
                df = pd.concat([df, new_recipe], ignore_index=True)
                df.to_csv(self.config.recipes_file, index=False)
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving recipe: {str(e)}")
            return False

    def save_feedback(self, recipe_title, feedback_text, sentiment):
        """Save user feedback"""
        try:
            df = pd.read_csv(self.config.feedback_file)
            new_feedback = pd.DataFrame([{
                'recipe_title': recipe_title,
                'feedback': feedback_text,
                'sentiment': sentiment,
                'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }])
            df = pd.concat([df, new_feedback], ignore_index=True)
            df.to_csv(self.config.feedback_file, index=False)
        except Exception as e:
            print(f"Error saving feedback: {str(e)}")

    def get_feedback(self):
        """Retrieve all feedback"""
        try:
            return pd.read_csv(self.config.feedback_file)
        except Exception as e:
            print(f"Error retrieving feedback: {str(e)}")
            return pd.DataFrame()

    def get_popular_recipes(self, limit=5):
        """Get most liked recipes"""
        try:
            df = pd.read_csv(self.config.recipes_file)
            # Convert likes to numeric, replacing any invalid values with 0
            df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0).astype(int)
            return df.nlargest(limit, 'likes')
        except Exception as e:
            print(f"Error getting popular recipes: {str(e)}")
            return pd.DataFrame()

    def update_recipe_likes(self, title):
        """Increment likes for a recipe"""
        try:
            df = pd.read_csv(self.config.recipes_file)
            df.loc[df['title'] == title, 'likes'] += 1
            df.to_csv(self.config.recipes_file, index=False)
        except Exception as e:
            print(f"Error updating likes: {str(e)}")