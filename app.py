import streamlit as st
import google.generativeai as genai
import random
import time

# Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# API Key Input
st.markdown("### 🔑 Gemini API Key Setup")
api_key = st.text_input(
    "Enter your Gemini API key:",
    type="password",
    help="Get your API key from https://aistudio.google.com/app/apikey",
    key="api_key_input"
)

if not api_key:
    st.warning("⚠️ Please enter your Gemini API key to use WiseBuddy")
    st.markdown("[How to get a Gemini API key](https://aistudio.google.com/app/apikey)")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello WiseBuddy")
    if not response.text:
        raise ValueError("No response from API")
    st.session_state.api_ready = True
    st.success("✅ API connected successfully!")
except Exception as e:
    st.error(f"❌ API Error: {e}")
    st.stop()

# CSS Styling
st.markdown("""
<style>
.big-font { font-size:28px; font-weight:bold; color:#2c3e50; text-align:center; margin-bottom:5px; }
.subtitle { text-align:center; color:#6c63ff; font-weight:500; margin-bottom:20px; }
.quote-container { background:#f0f0ff; padding:15px; border-radius:15px; margin-bottom:20px; }
.user-bubble { background:#d0f0c0; padding:12px 16px; border-radius:18px 18px 0 18px; max-width:70%; margin-left:auto; margin-bottom:10px; }
.bot-bubble { background:#e0d4f7; padding:12px 16px; border-radius:18px 18px 18px 0; max-width:70%; margin-right:auto; margin-bottom:10px; }
.typing-indicator { background:#e0d4f7; padding:10px 16px; border-radius:15px; width:60px; display:flex; gap:5px; }
.typing-dot { width:8px; height:8px; background:#6c63ff; border-radius:50%; animation: blink 1.2s infinite; }
@keyframes blink { 0% {opacity: 0.2;} 50% {opacity: 1;} 100% {opacity: 0.2;} }
</style>
""", unsafe_allow_html=True)

# Title and Quote
st.markdown('<p class="big-font">💬 WiseBuddy 🧠</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI companion for thoughtful advice</p>', unsafe_allow_html=True)

quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now."
]
st.markdown(f'<div class="quote-container"><em>{random.choice(quotes)}</em></div>', unsafe_allow_html=True)

# Chat State Initialization
def init_state():
    return {
        "history": [],
        "category": "🌟 Motivation & Positivity",
        "is_processing": False
    }

if "app_state" not in st.session_state:
    st.session_state.app_state = init_state()

# Control Panel
col1, col2 = st.columns([3,1])
with col1:
    category = st.selectbox(
        "📝 Choose your advice style:",
        ["🌟 Motivation & Positivity", "💡 Business & Wealth", "❤️ Love & Relationships", "🧘 Mindfulness & Peace"],
        index=0
    )
with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.app_state = init_state()
        st.experimental_rerun()

if category != st.session_state.app_state["category"]:
    st.session_state.app_state["category"] = category
    st.session_state.app_state["history"].append(("bot", f"Switched to **{category}** advice. How can I help?"))

# Message Display
st.markdown('<div style="background:white;border-radius:15px;padding:15px;">', unsafe_allow_html=True)

if not st.session_state.app_state["history"]:
    st.session_state.app_state["history"].append(("bot", f"Hi! I'm WiseBuddy, ready to help with **{category}** advice. How can I assist?"))

for speaker, message in st.session_state.app_state["history"]:
    if speaker == "user":
        st.markdown(f'<div class="user-bubble"><strong>You:</strong><br>{message}</div>', unsafe_allow_html=True)
    elif speaker == "bot":
        st.markdown(f'<div class="bot-bubble"><strong>WiseBuddy:</strong><br>{message}</div>', unsafe_allow_html=True)
    elif speaker == "typing":
        st.markdown('<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat Input
user_input = st.chat_input("💬 Type something here...")

if user_input and not st.session_state.app_state["is_processing"]:
    st.session_state.app_state["history"].append(("user", user_input))
    st.session_state.app_state["history"].append(("typing", ""))
    st.session_state.app_state["is_processing"] = True
    st.experimental_rerun()

# Handle Response
if st.session_state.app_state["is_processing"] and st.session_state.app_state["history"][-1][0] == "typing":
    try:
        prompt = f"You are WiseBuddy, giving advice on {st.session_state.app_state['category']}. Respond helpfully to: {st.session_state.app_state['history'][-2][1]}"
        response = model.generate_content(prompt)
        reply = response.text or "I'm here to help! Could you clarify your question?"
        st.session_state.app_state["history"].pop()  # remove typing
        st.session_state.app_state["history"].append(("bot", reply))
    except Exception as e:
        st.session_state.app_state["history"].pop()
        st.session_state.app_state["history"].append(("bot", f"⚠️ Oops: {str(e)}"))
    finally:
        st.session_state.app_state["is_processing"] = False
        st.experimental_rerun()

# Footer
st.markdown('<div class="footer">WiseBuddy 🧠 • Powered by Gemini</div>', unsafe_allow_html=True)
