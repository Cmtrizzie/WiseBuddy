import streamlit as st
import google.generativeai as genai

# Configure your actual Gemini API key
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")

model = genai.GenerativeModel('gemini-1.5-flash')

# Page configuration
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# Custom styling
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    .big-font {
        font-size:26px !important;
        font-weight: bold;
        color: #2c3e50;
    }
    .advice-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        color: #333333;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<p class="big-font">💬 Welcome to <span style="color:#6c63ff;">WiseBuddy</span> 🧠</p>', unsafe_allow_html=True)
st.write("Your friendly AI advice bot. Choose your advice style and tell me what’s on your mind.")

# Advice Category Selection
category = st.selectbox("📝 Choose your advice style:", [
    "🌟 Motivation & Positivity",
    "💡 Business & Wealth",
    "❤️ Love & Relationships",
    "🧘 Mindfulness & Peace"
])

# User Input
user_input = st.text_input("💭 What's on your mind?")

if user_input:
    with st.spinner("WiseBuddy is thinking..."):
        prompt = f"You are WiseBuddy, a wise and kind chatbot specializing in {category}. Give short, helpful advice about: {user_input}"
        response = model.generate_content(prompt)
        st.markdown(f'<div class="advice-box">{response.text}</div>', unsafe_allow_html=True)
