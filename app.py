"""
Main application module for Smart Recipe Generator.
Integrates video processing, recipe generation, and user interaction.
"""

import streamlit as st
import requests
import json
from typing import Optional, Tuple, Dict
from faster_whisper import WhisperModel
import torch
from yt_dlp import YoutubeDL
from slugify import slugify
from pathlib import Path

from database import RecipeDatabase
from utils import FeedbackManager, ImageProcessor
from logger import setup_logger

logger = setup_logger(__name__)

class RecipeGeneratorApp:
    """Main application class for Smart Recipe Generator."""
    
    def __init__(self):
        self.setup_config()
        self.initialize_components()
        self.setup_page_config()
        self.apply_styling()
        
    def setup_config(self):
        """Initialize application configuration."""
        self.GEMINI_API_KEY = "YOUR_API_KEY"
        self.GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        
        # GPU configuration
        if torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(0.4)
            self.device = "cuda"
        else:
            self.device = "cpu"
        logger.info(f"Using device: {self.device}")
        
    def initialize_components(self):
        """Initialize main application components."""
        self.db = RecipeDatabase()
        self.feedback_manager = FeedbackManager()
        self.image_processor = ImageProcessor()
        
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Smart Recipe Generator",
            page_icon="🍳",
            layout="wide",
        )
        
    def apply_styling(self):
        """Apply custom CSS styling."""
        st.markdown(self._get_custom_css(), unsafe_allow_html=True)
        
    @staticmethod
    def _get_custom_css() -> str:
        """Return custom CSS for styling."""
        return """
            <style>
            /* Modern gradient background with subtle animation */
            .stApp {
                background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
            }
            
            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            /* Main content styling */
            .main {
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            /* Modern button styling */
            .stButton>button {
                width: 100%;
                background: linear-gradient(45deg, #FF416C, #FF4B2B);
                color: white;
                border-radius: 12px;
                padding: 1rem 2rem;
                font-weight: 600;
                border: none;
                box-shadow: 0 10px 20px rgba(255, 65, 108, 0.3);
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .stButton>button:hover {
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 15px 30px rgba(255, 65, 108, 0.4);
            }
            
            .stButton>button:active {
                transform: translateY(1px);
            }
            
            /* Glass-morphism recipe card */
            .recipe-card {
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 24px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.18);
                transition: transform 0.3s ease;
                margin: 1rem 0;
            }
            
            .recipe-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(31, 38, 135, 0.25);
            }
            
            /* Title styling with animated gradient */
            .title-text {
                background: linear-gradient(300deg, #FF416C, #FF4B2B, #FFB199);
                background-size: 200% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3.5rem;
                font-weight: 800;
                text-align: center;
                animation: shine 3s linear infinite;
                margin-bottom: 2rem;
            }
            
            @keyframes shine {
                to {
                    background-position: 200% center;
                }
            }
            
            /* Input fields styling */
            .stTextInput>div>div>input {
                border-radius: 12px;
                border: 2px solid rgba(255, 65, 108, 0.2);
                padding: 1rem;
                background: rgba(255, 255, 255, 0.9);
                transition: all 0.3s ease;
            }
            
            .stTextInput>div>div>input:focus {
                border-color: #FF416C;
                box-shadow: 0 0 15px rgba(255, 65, 108, 0.2);
            }
            
            /* Select box styling */
            .stSelectbox>div>div>div {
                border-radius: 12px;
                border: 2px solid rgba(255, 65, 108, 0.2);
                background: rgba(255, 255, 255, 0.9);
            }
            
            .stSelectbox>div>div>div:hover {
                border-color: #FF416C;
            }
            
            /* Feedback section styling */
            .feedback-container {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 16px;
                padding: 1.5rem;
                margin: 1rem 0;
                border-left: 5px solid #FF416C;
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(45deg, #FF416C, #FF4B2B);
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(45deg, #FF4B2B, #FF416C);
            }
            
            /* Radio button styling */
            .stRadio>div {
                background: rgba(255, 255, 255, 0.9);
                padding: 1rem;
                border-radius: 12px;
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
            
            /* Spinner animation */
            .stSpinner>div {
                border-color: #FF416C #FF4B2B #23a6d5 #23d5ab;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                to {
                    transform: rotate(360deg);
                }
            }
            
            /* Success message styling */
            .stSuccess {
                background: rgba(40, 167, 69, 0.2);
                border: none;
                border-radius: 12px;
                padding: 1rem;
                color: #28a745;
                font-weight: 600;
            }
            
            /* Error message styling */
            .stError {
                background: rgba(220, 53, 69, 0.2);
                border: none;
                border-radius: 12px;
                padding: 1rem;
                color: #dc3545;
                font-weight: 600;
            }
            
            /* Markdown text styling */
            .stMarkdown {
                color: #2c3e50;
                line-height: 1.6;
                font-size: 1.1rem;
            }
            
            /* Code block styling */
            code {
                background: rgba(255, 255, 255, 0.9);
                padding: 0.2rem 0.4rem;
                border-radius: 4px;
                color: #FF416C;
                font-family: 'Courier New', monospace;
            }
            </style>
        """
    
    def get_video_audio(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract audio from YouTube video URL.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            Tuple[Optional[str], Optional[str]]: Video title and audio URL
        """
        try:
            with YoutubeDL({'format': 'bestaudio'}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info['title'], info['url']
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            st.error(f"Error processing video: {str(e)}")
            return None, None
            
    def audio_to_transcript(self, audio_url: str, language: str) -> Optional[str]:
        """
        Convert audio to transcript using Whisper model.
        
        Args:
            audio_url (str): URL to audio file
            language (str): Target language code
            
        Returns:
            Optional[str]: Transcribed text
        """
        try:
            model = WhisperModel("base", device=self.device)
            segments, _ = model.transcribe(audio_url, language=language)
            return " ".join([segment.text for segment in segments])
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            st.error(f"Transcription failed: {str(e)}")
            return None
            
    def generate_recipe(self, text: str) -> Optional[str]:
        """
        Generate recipe from transcript using Gemini API.
        
        Args:
            text (str): Transcribed text
            
        Returns:
            Optional[str]: Generated recipe text
        """
        headers = {"Content-Type": "application/json"}
        prompt = self._create_recipe_prompt(text)
        
        try:
            response = requests.post(
                f"{self.GEMINI_URL}?key={self.GEMINI_API_KEY}",
                headers=headers,
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f"API Error: {response.text}")
                st.error("Failed to generate recipe")
                return None
                
        except Exception as e:
            logger.error(f"Recipe generation error: {str(e)}")
            st.error("Failed to generate recipe")
            return None
            
    @staticmethod
    def _create_recipe_prompt(text: str) -> str:
        """Create prompt for recipe generation."""
        return f"""Create a detailed recipe from this cooking video with:
        1. Title and brief introduction
        2. Ingredients list with measurements
        3. Step-by-step instructions
        4. Cooking tips and variations
        5. Serving size and time required
        
        Make it engaging and easy to follow!
        
        Transcript: {text}"""
        
    def run(self):
        """Run the main application."""
        self.render_header()
        language = self.render_language_selector()
        url = self.render_url_input()
        
        if url and st.button("🪄 Generate Magic Recipe"):
            self.process_video(url, language)
            
        self.render_feedback_section()
        self.render_footer()
        
    def render_header(self):
        """Render application header."""
        st.markdown("<h1 class='title-text'>🍳 Smart Recipe Generator</h1>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='background: linear-gradient(45deg, #FF416C, #FF4B2B); 
                        padding: 15px; 
                        border-radius: 15px; 
                        color: white;
                        margin-bottom: 30px;
                        text-align: center;
                        font-size: 1.2rem;'>
                Transform any cooking video into a detailed recipe with AI magic! ✨
            </div>
            """,
            unsafe_allow_html=True
        )
        
    def render_language_selector(self) -> str:
        """Render language selection dropdown."""
        return st.selectbox(
            "Select Language for Transcription and Recipe:",
            ["en", "es", "fr", "de", "zh"],
            index=0,
            format_func=lambda x: {
                "en": "English",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "zh": "Chinese"
            }[x]
        )
        
    def render_url_input(self) -> str:
        """Render URL input field."""
        return st.text_input(
            '🎥 Paste YouTube Video URL',
            placeholder="https://youtube.com/...",
            help="Enter a YouTube cooking video URL to get started!"
        )
        
    def process_video(self, url: str, language: str):
        """Process video and generate recipe."""
        with st.spinner("✨ Cooking up your recipe..."):
            video_title, audio_url = self.get_video_audio(url)
            
            if audio_url:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📺 Video Source")
                    st.video(url)
                
                with col2:
                    st.markdown("### 📝 AI Generated Recipe")
                    transcript = self.audio_to_transcript(audio_url, language)
                    if transcript:
                        recipe = self.generate_recipe(transcript)
                        if recipe:
                            self.render_recipe(recipe, video_title)
                            self.handle_recipe_actions(recipe, video_title)
                            
    def render_recipe(self, recipe: str, title: str):
        """Render recipe card and save to database."""
        st.markdown(
            f"""
            <div class="recipe-card">
                {recipe}
            </div>
            """,
            unsafe_allow_html=True
        )
        self.db.save_recipe(title, "", recipe)
        
    def handle_recipe_actions(self, recipe: str, title: str):
        """Handle recipe-related actions."""
        filename = f"{slugify(title)}_recipe.txt"
        st.download_button(
            "📥 Save Recipe",
            recipe,
            file_name=filename,
            mime="text/plain"
        )
        
        st.markdown("### 💬 Feedback")
        feedback = st.text_area("What do you think about this recipe?")
        sentiment = st.radio("Sentiment", ["Positive", "Neutral", "Negative"])
        
        if st.button("Submit Feedback"):
            if self.feedback_manager.save_feedback(title, feedback, sentiment):
                st.success("Thank you for your feedback!")
            else:
                st.error("Failed to save feedback")
                
    def render_feedback_section(self):
        """Render feedback section."""
        st.markdown("## 📝 User Feedback")
        feedback_data = self.db.get_feedback()
        for _, row in feedback_data.iterrows():
            st.markdown(
                f"""
                <div class="feedback-container">
                    <h3>{row['recipe_title']}</h3>
                    <p>{row['feedback']}</p>
                    <span style="color: {'#28a745' if row['sentiment'] == 'Positive' 
                                      else '#dc3545' if row['sentiment'] == 'Negative' 
                                      else '#ffc107'}">
                        {row['sentiment']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    def render_footer(self):
        """Render application footer."""
        st.markdown(
            """
            <div style='text-align: center; 
                        background: linear-gradient(45deg, #FF416C, #FF4B2B);
                        color: white;
                        padding: 20px;
                        border-radius: 15px;
                        margin-top: 50px;'>
                Made with 🔥 for passionate home chefs
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    app = RecipeGeneratorApp()
    app.run()
