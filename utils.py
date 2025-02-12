"""
Utility functions for image processing and data management.
Provides core functionality for frame processing and feedback handling.
"""

import os
from typing import Any, Dict, Union
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import pandas as pd
from logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

class ImageProcessor:
    """Handles all image processing operations for the application."""
    
    @staticmethod
    def process_frame(frame: np.ndarray, model: Any) -> np.ndarray:
        """
        Process a single frame for ingredient detection.
        
        Args:
            frame (np.ndarray): Input frame in BGR format
            model (Any): Trained model for inference
            
        Returns:
            np.ndarray: Processed frame ready for model inference
        """
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            img = img.resize((224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            return preprocess_input(x)
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            raise

class FeedbackManager:
    """Manages user feedback operations."""
    
    def __init__(self, feedback_file: str = "feedback_data.csv"):
        self.feedback_file = feedback_file
        
    def save_feedback(self, 
                     recipe_title: str, 
                     feedback: str, 
                     sentiment: str) -> bool:
        """
        Save user feedback and sentiment to CSV.
        
        Args:
            recipe_title (str): Title of the recipe
            feedback (str): User feedback text
            sentiment (str): Sentiment classification
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            feedback_data = {
                'recipe_title': [recipe_title],
                'feedback': [feedback],
                'sentiment': [sentiment],
                'timestamp': [pd.Timestamp.now()]
            }
            df = pd.DataFrame(feedback_data)
            
            if os.path.exists(self.feedback_file):
                df.to_csv(self.feedback_file, mode='a', header=False, index=False)
            else:
                df.to_csv(self.feedback_file, index=False)
            return True
            
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            return False