# ChefLens - Smart Recipe Generator

## 📌 Project Overview
ChefLens is a **Smart Recipe Generator** that processes cooking videos and extracts detailed recipes using AI. The application integrates video processing, recipe generation, and user interaction through an intuitive web interface built with **Streamlit**.

## ✨ Features
- 🎥 **Video Processing**: Extracts audio from YouTube videos and transcribes it using a Whisper model.
- 🍽 **Recipe Generation**: Utilizes the Gemini API to generate recipes from transcribed text.
- 📝 **User Feedback**: Allows users to submit feedback on generated recipes, which is stored in a database.
- 📊 **Database Management**: Manages recipes, feedback, and leaderboard data using **SQLite**.
- 📜 **Logging**: Tracks application events and errors for debugging and monitoring.

## 🛠️ Installation & Setup

### Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SuhasA72/ChefLens.git
   cd ChefLens
   ```
2. **Create a Virtual Environment (Optional but Recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Up API Key**: Configure the **Gemini API key** in `app.py`.
5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
6. **Access the Application**: Open the provided URL in your web browser.

## 🚀 Usage Guide
1. **Start ChefLens**: Run `streamlit run app.py` and access the app in your browser.
2. **Enter Video URL**: Paste a YouTube video link to extract and process its audio.
3. **Generate Recipe**: Click the **"Generate Magic Recipe"** button to create a recipe.
4. **Provide Feedback**: Submit feedback on the generated recipe for future improvements.

## 🏗️ Tech Stack
- **Python**: Core programming language
- **Streamlit**: Web application framework
- **TensorFlow & Keras**: Image processing and model inference
- **Pandas**: Data manipulation and storage
- **SQLite**: Database management
- **Logging**: Python's built-in logging module

## 🔗 API References
- **Gemini API**: Used for generating recipes from transcribed text.

## 🏆 Workflow
1. **Video Processing**: Extracts and transcribes audio from a YouTube video.
2. **Recipe Generation**: Sends the transcribed text to the **Gemini API** to generate a structured recipe.
3. **User Interaction**: Users can view, download, and provide feedback on recipes.
4. **Data Management**: Recipes and feedback are stored in a **SQLite database**.
5. **Logging & Monitoring**: Keeps track of errors and events for debugging.

## 🤝 Contributing
1. **Fork the Repository**
2. **Create a Branch**: `git checkout -b feature-branch`
3. **Commit Changes**: `git commit -m "Add new feature"`
4. **Push to GitHub**: `git push origin feature-branch`
5. **Submit a Pull Request**

## 📜 License
This project is licensed under the **MIT License**.

---
### 🎯 Developed by [SuhasA72](https://github.com/SuhasA72)
📩 Feel free to contribute, report issues, or suggest improvements!

