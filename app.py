import streamlit as st
import google.generativeai as genai
import random

# 👉 Configure your actual Gemini API key
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")
model = genai.GenerativeModel('gemini-1.5-flash')

# 👉 Streamlit page setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 CSS Styling
st.markdown("""
    <style>
    .big-font { font-size:26px !important; font-weight:bold; color:#2c3e50; }
    .advice-box { background-color:#fff; padding:15px; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1); color:#333; font-size:17px; margin-top:10px; }
    </style>
""", unsafe_allow_html=True)

# 👉 Title + Quote of the Day
st.markdown('<p class="big-font">💬 Welcome to <span style="color:#6c63ff;">WiseBuddy</span> 🧠</p>', unsafe_allow_html=True)

quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now."
]
st.markdown(f'<div style="background-color:#e6e6fa;padding:10px;border-radius:10px;text-align:center;"><em>{random.choice(quotes)}</em></div>', unsafe_allow_html=True)

# 👉 Category Select
category = st.selectbox("📝 Choose your advice style:", [
    "🌟 Motivation & Positivity",
    "💡 Business & Wealth",
    "❤️ Love & Relationships",
    "🧘 Mindfulness & Peace"
])

# 👉 Initialize Chat History
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 👉 User Input Box
user_input = st.text_input("💭 Type your message here:")

# 👉 When User Submits:
if user_input:
    with st.spinner("WiseBuddy is thinking..."):
        prompt = f"You are WiseBuddy, a friendly advice chatbot specializing in {category}. Respond kindly to: {user_input}"
        response = model.generate_content(prompt)
        answer = response.text

        # Save to history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("WiseBuddy 🤖", answer))

# 👉 Display Chat History
for speaker, message in st.session_state.chat_history:
    st.markdown(f'<div class="advice-box"><strong>{speaker}:</strong><br>{message}</div>', unsafe_allow_html=True)
