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
import random

# List of daily motivational quotes
quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now."
]

# Pick a random quote
quote_of_the_day = random.choice(quotes)

# Display the quote
st.markdown(f'<div style="background-color:#e6e6fa;padding:15px;border-radius:10px;text-align:center;"><em>{quote_of_the_day}</em></div>', unsafe_allow_html=True)
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
        
        # ✅ Display the advice inside advice-box
        st.markdown(f'<div class="advice-box">{response.text}</div>', unsafe_allow_html=True)

        # ✅ Display copyable code box
        st.code(response.text, language='')
