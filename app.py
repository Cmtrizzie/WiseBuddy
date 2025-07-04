import streamlit as st import google.generativeai as genai import random

👉 Configure your Gemini API Key

genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4") model = genai.GenerativeModel('gemini-1.5-flash')  # Or use 'models/gemini-pro' if needed

👉 Streamlit Page Setup

st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

👉 Basic CSS Styling

st.markdown("""

<style>
.big-font {
    font-size: 28px !important;
    font-weight: bold;
    color: #2c3e50;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #6c63ff;
    margin-bottom: 20px;
}

.user-bubble {
    background-color: #d0f0c0;
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
    margin-left: auto;
}

.bot-bubble {
    background-color: #e0d4f7;
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
    margin-right: auto;
}

</style>""", unsafe_allow_html=True)

👉 Title and Quote

st.markdown('<p class="big-font">💬 WiseBuddy 🧠</p>', unsafe_allow_html=True) st.markdown('<p class="subtitle">Your AI companion for thoughtful advice</p>', unsafe_allow_html=True)

quotes = [ "🌟 Believe you can and you're halfway there.", "🚀 Success is the sum of small efforts repeated daily.", "💡 The best way to predict the future is to create it.", "❤️ You are stronger than you think." ] st.markdown(f"<div style='text-align:center; margin-bottom:15px;'>{random.choice(quotes)}</div>", unsafe_allow_html=True)

👉 Initialize Chat State

if "history" not in st.session_state: st.session_state.history = []

if "chat_session" not in st.session_state: st.session_state.chat_session = model.start_chat(history=[])

👉 Display Chat History

for speaker, message in st.session_state.history: if speaker == "user": st.markdown(f"<div class='user-bubble'><strong>You:</strong><br>{message}</div>", unsafe_allow_html=True) else: st.markdown(f"<div class='bot-bubble'><strong>WiseBuddy:</strong><br>{message}</div>", unsafe_allow_html=True)

👉 User Input

user_input = st.chat_input("💭 Type your message here...")

👉 Process Input

if user_input: st.session_state.history.append(("user", user_input))

prompt = f"You are WiseBuddy, an AI specializing in friendly, thoughtful advice. Respond to: {user_input}"

try:
    response = st.session_state.chat_session.send_message(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.8,
            max_output_tokens=500
        )
    )
    bot_reply = response.text
except Exception as e:
    bot_reply = "⚠️ Sorry, I'm having trouble responding right now."

st.session_state.history.append(("bot", bot_reply))
st.experimental_rerun()

👉 Footer

st.markdown("""

<div style='text-align:center; margin-top:30px; color: #888;'>WiseBuddy 🧠 • Powered by Gemini</div>
""", unsafe_allow_html=True)
