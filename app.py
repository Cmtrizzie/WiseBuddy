import streamlit as st
import google.generativeai as genai
import os
# from dotenv import load_dotenv # Can remove this line
# from pathlib import Path # Can remove this line
import time

# --- Configuration ---
# BASE_DIR = Path(__file__).resolve().parent # Can remove this line
# DOTENV_PATH = BASE_DIR / ".env" # Can remove this line

# --- Debugging Load_dotenv (REMOVE THESE LINES FOR DEPLOYMENT) ---
# dotenv_loaded_successfully = False # REMOVE
# if DOTENV_PATH.exists(): # REMOVE
#     print(f"DEBUG: .env file exists at {DOTENV_PATH}") # REMOVE
#     st.sidebar.write(f"DEBUG: .env file exists at `{DOTENV_PATH}`") # REMOVE
#     dotenv_loaded_successfully = load_dotenv(dotenv_path=DOTENV_PATH) # REMOVE
# else: # REMOVE
#     print(f"DEBUG: .env file NOT found at {DOTENV_PATH}") # REMOVE
#     st.sidebar.write(f"DEBUG: .env file NOT found at `{DOTENV_PATH}`") # REMOVE
# st.sidebar.write(f"DEBUG: .env file loaded? **{dotenv_loaded_successfully}**") # REMOVE
# --- End Debugging ---


# Gemini Model Name
MODEL_NAME = "gemini-1.5-flash"

# WiseBuddy's Persona/System Instruction
SYSTEM_INSTRUCTION = """
You are WiseBuddy, a friendly, helpful, and knowledgeable AI assistant.
Your goal is to provide concise, accurate, and relevant information.
Maintain a positive and approachable tone.
If you don't know the answer, politely state that you cannot provide information on that topic.
Always prioritize user safety and ethical responses.
"""

# --- API Key Management (Simplified for Streamlit Cloud) ---
GEMINI_API_KEY = None
try:
    # This is the primary way to get secrets in Streamlit Cloud
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        # Fallback for local testing if you choose to set environment vars manually
        # This will NOT work on Streamlit Cloud without st.secrets
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY:
            st.sidebar.write("DEBUG: API Key found via os.getenv() (for local development).")
        else:
            st.sidebar.write("DEBUG: API Key NOT found via os.getenv().")
    else:
        st.sidebar.write("DEBUG: API Key found in Streamlit Secrets.")

except Exception as e:
    st.sidebar.write(f"DEBUG: Error accessing st.secrets or environment variable: {e}")
    GEMINI_API_KEY = None


# --- Final check and stop if key is missing ---
if not GEMINI_API_KEY:
    st.error("🚨 Gemini API key not found. Please set `GEMINI_API_KEY` in your Streamlit Cloud secrets.")
    st.info("For Streamlit Cloud deployment, add `GEMINI_API_KEY` to your app's secrets.")
    st.stop() # Stop the app if no API key is found
else:
    st.sidebar.success("DEBUG: Gemini API Key successfully loaded! 🎉")


genai.configure(api_key=GEMINI_API_KEY)

# ... (rest of your app.py code remains the same) ...

