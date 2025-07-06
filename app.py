import streamlit as st
import google.generativeai as genai
import os

# Set page config
st.set_page_config(page_title="Gemini 1.5 Flash Chatbot", page_icon="🚀")

# --- API Key Handling ---
api_key = None

# Try Streamlit secrets first
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("API key loaded from Streamlit secrets")
except (KeyError, FileNotFoundError):
    # Fallback to environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.sidebar.info("API key loaded from environment variable")
    else:
        st.sidebar.error("API key not found! Please add it to secrets")

if not api_key:
    # Show input field if no key found
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if not api_key:
        st.warning("⚠️ Please provide your Gemini API key to continue")
        st.stop()

# Configure Gemini with the API key
genai.configure(api_key=api_key)
