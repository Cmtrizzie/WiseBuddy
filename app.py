import streamlit as st
import google.generativeai as genai
import random

# Configure your actual Gemini API key
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")

model = genai.GenerativeModel('gemini-1.5-flash')

# Page config
st.set_page_config(page_title="WiseBuddy", layout="centered")

# 🌟 Daily Random Quote
quotes = [
    "Believe you can and you're halfway there.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "The best investment you can make is in yourself.",
    "In the middle of every difficulty lies opportunity.",
    "Love yourself first and everything else falls into line.",
    "Happiness is not something ready-made. It comes from your own actions.",
    "Patience is the key to joy.",
    "The biggest risk is not taking any risk."
]
daily_quote = random.choice(quotes)
st.markdown(f"""
<div style='background-color:#f0f0f0; padding:10px; border-radius:10px; text-align:center; font-size:18px;'>
<em>{daily_quote}</em>
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title
st.markdown("<h1 style='text-align:center;'>WiseBuddy Chat</h1>", unsafe_allow_html=True)
st.write("Chat with WiseBuddy about anything—life, goals, or just venting.")

# Advice category
category = st.selectbox("Choose your advice style:", [
    "Motivation & Positivity",
    "Business & Wealth",
    "Love & Relationships",
    "Mindfulness & Peace"
])

# Text input and button (side by side)
col1, col2 = st.columns([5,1])

with col1:
    user_input = st.text_input("Type here...", key="input_text", label_visibility="collapsed")
with col2:
    send_clicked = st.button("Send")

# Process user message safely
if send_clicked and user_input:
    with st.spinner("WiseBuddy is thinking..."):
        prompt = f"You are WiseBuddy, giving advice about {category}. Respond to: {user_input}"
        response = model.generate_content(prompt)
        reply = response.text

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("WiseBuddy", reply))

    # Just rerun the app to clear input safely
    st.experimental_rerun()

# 🖥️ Scrollable chat box
st.markdown("""
<div style='max-height:400px; overflow-y: auto; padding:10px; border:1px solid #ddd; border-radius:10px; background-color:#fff;'>
""", unsafe_allow_html=True)

for speaker, message in st.session_state.chat_history:
    st.markdown(f"""
    <div style='background-color:#f9f9f9; padding:10px; margin-bottom:10px; border-radius:8px;'>
    <strong>{speaker}:</strong><br>{message}
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
