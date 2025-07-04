import streamlit as st
import google.generativeai as genai
import random
import time
import os

# 👉 Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 API Key Setup
st.markdown("### 🔑 Gemini API Key Setup")
api_key = st.text_input("Enter your Gemini API key:", type="password", 
                        help="Get your API key from https://aistudio.google.com/app/apikey",
                        key="api_key_input")

if not api_key:
    st.warning("⚠️ Please enter your Gemini API key to use WiseBuddy.")
    st.markdown("[How to get a Gemini API key](https://aistudio.google.com/app/apikey)")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    test_response = model.generate_content("Hello")
    if not test_response.text:
        raise ValueError("API responded with empty text.")
    st.session_state.api_ready = True
    st.success("✅ Gemini API connected!")
except Exception as e:
    st.error(f"❌ API error: {str(e)}")
    st.stop()

# 👉 CSS Styling
st.markdown("""
    <style>
    body { font-family: 'Poppins', sans-serif; }
    .big-font { font-size:28px; font-weight:700; color:#2c3e50; text-align:center; }
    .subtitle { text-align:center; color:#6c63ff; font-weight:500; margin-bottom:20px; }
    .quote-container { background: #e6e6fa; padding:15px; border-radius:18px; text-align:center; margin-bottom:25px; }
    .quote-text { font-style: italic; font-size: 16px; color: #4a4a7d; }
    .chat-container { background:white; border-radius:20px; padding:20px; box-shadow:0 8px 30px rgba(0,0,0,0.08); margin-bottom:20px; }
    .message-area { height:55vh; overflow-y:auto; padding:15px; background:#fafaff; border-radius:15px; }
    .user-bubble { background:linear-gradient(135deg,#d0f0c0,#b8e994); padding:16px 20px; border-radius:24px 24px 0 24px; max-width:80%; margin-left:auto; margin-bottom:15px; }
    .bot-bubble { background:linear-gradient(135deg,#e0d4f7,#cbb2fe); padding:16px 20px; border-radius:24px 24px 24px 0; max-width:80%; margin-right:auto; margin-bottom:15px; }
    .footer { text-align:center; margin-top:30px; color:#7b7b7b; font-size:14px; }
    </style>
""", unsafe_allow_html=True)

# 👉 Title + Quote
st.markdown('<p class="big-font">💬 WiseBuddy 🧠</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI companion for thoughtful advice</p>', unsafe_allow_html=True)

quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now.",
    "🌱 Growth begins at the end of your comfort zone.",
    "🌈 After every storm comes a rainbow of possibilities."
]
st.markdown(f"""
    <div class="quote-container"><p class="quote-text">{random.choice(quotes)}</p></div>
""", unsafe_allow_html=True)

# 👉 Initialize State
def initialize_chat():
    return {
        "history": [],
        "current_category": "🌟 Motivation & Positivity",
        "is_processing": False
    }

if "app_state" not in st.session_state:
    st.session_state.app_state = initialize_chat()

# 👉 Control Panel
new_category = st.selectbox(
    "📝 Choose your advice style:",
    [
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace",
        "🎯 Goal Setting",
        "🔄 Life Transitions"
    ],
    index=[
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace",
        "🎯 Goal Setting",
        "🔄 Life Transitions"
    ].index(st.session_state.app_state["current_category"])
)

if st.button("🗑️ Clear Chat"):
    st.session_state.app_state = initialize_chat()
    st.session_state.app_state["history"].append(
        ("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.app_state['current_category']}**. How can I help today?")
    )
    st.experimental_rerun()

if new_category != st.session_state.app_state["current_category"]:
    st.session_state.app_state["current_category"] = new_category
    st.session_state.app_state["history"].append(
        ("bot", f"Switched to **{new_category}** mode. How can I assist you?")
    )

# 👉 Chat Display
st.markdown('<div class="chat-container"><div class="message-area">', unsafe_allow_html=True)

if not st.session_state.app_state["history"]:
    st.session_state.app_state["history"].append(
        ("bot", f"Hello! I'm WiseBuddy, your AI advisor in **{st.session_state.app_state['current_category']}**. How can I assist you today?")
    )

for speaker, message in st.session_state.app_state["history"]:
    if speaker == "user":
        st.markdown(f'<div class="user-bubble"><strong>You:</strong><br>{message}</div>', unsafe_allow_html=True)
    elif speaker == "bot":
        st.markdown(f'<div class="bot-bubble"><strong>WiseBuddy:</strong><br>{message}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# 👉 User Input & Response
user_input = st.chat_input("💭 Type your message here...")

if user_input and not st.session_state.app_state["is_processing"]:
    st.session_state.app_state["is_processing"] = True
    st.session_state.app_state["history"].append(("user", user_input))
    st.session_state.app_state["history"].append(("bot", "🤖 Thinking..."))
    st.experimental_rerun()

if st.session_state.app_state["is_processing"] and st.session_state.app_state["history"][-1][1] == "🤖 Thinking...":
    try:
        instruction = (
            f"You are WiseBuddy, a friendly advisor in {st.session_state.app_state['current_category']}.\n"
            "Be supportive, concise, friendly, and helpful.\n"
        )
        response = model.generate_content(
            user_input,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=500
            ),
            system_instruction=instruction
        )
        reply = response.text.strip() or "🙂 I'm here to help!"
        st.session_state.app_state["history"][-1] = ("bot", reply)
    except Exception as e:
        st.session_state.app_state["history"][-1] = ("bot", "⚠️ Sorry, I ran into an issue.")
    finally:
        st.session_state.app_state["is_processing"] = False
        st.experimental_rerun()

# 👉 Footer
st.markdown("""
    <div class="footer">
        WiseBuddy 🧠 • Your AI companion for thoughtful advice • Powered by Gemini
    </div>
""", unsafe_allow_html=True)
