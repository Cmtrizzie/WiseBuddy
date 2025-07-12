import streamlit as st
import google.generativeai as genai
import os

# Minimal API Key Setup (just to prevent the app from stopping if not found)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.warning("API key not found, but continuing for testing UI render.")
    # st.stop() # DO NOT stop for this test

# Display a simple message
st.title("Hello, WiseBuddy Test!")
st.write("If you see this, Streamlit is working.")

# Try a simple text input just to see if it renders
user_input = st.text_input("Enter something:")
if user_input:
    st.write(f"You entered: {user_input}")

# Try to initialize genai, even if API key is missing, it shouldn't cause a blank screen here
try:
    genai.configure(api_key=GEMINI_API_KEY if GEMINI_API_KEY else "dummy_key_for_testing")
    st.sidebar.success("GenAI configured (possibly with dummy key).")
except Exception as e:
    st.sidebar.error(f"GenAI config error: {e}")

# The rest of your app.py content would go after this (but keep it minimal for now)
