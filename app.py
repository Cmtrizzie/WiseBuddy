import streamlit as st import google.generativeai as genai import random

Set page configuration

st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

API Key input

st.markdown("### 🔑 Gemini API Key Setup") api_key = st.text_input("Enter your Gemini API key:", type="password", help="Get your API key from https://aistudio.google.com/app/apikey", key="api_key_input")

if not api_key: st.warning("⚠️ Please enter your Gemini API key to use WiseBuddy") st.markdown("How to get a Gemini API key") st.stop()

try: genai.configure(api_key=api_key) model = genai.GenerativeModel('gemini-1.5-flash') response_test = model.generate_content("Hello") if not response_test.text: raise ValueError("API key invalid or no response") st.success("✅ API connected successfully!") except Exception as e: st.error(f"❌ API Error: {str(e)}") st.stop()

CSS Styling

st.markdown(""" <style> .big-font { font-size:28px !important; font-weight:700; color:#2c3e50; text-align:center; margin-bottom:5px; } .subtitle { text-align:center; color:#6c63ff; font-weight:500; margin-bottom:20px; } .chat-container { background: white; border-radius: 20px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); margin-bottom: 20px; } .message-area { height: 55vh; overflow-y: auto; padding: 15px; margin-bottom: 20px; background: #fafaff; border-radius: 15px; border: 1px solid rgba(0,0,0,0.03); } .user-bubble { background: linear-gradient(135deg, #d0f0c0 0%, #b8e994 100%); padding: 16px 20px; border-radius: 24px 24px 0 24px; max-width: 80%; font-size: 16px; margin-left: auto; margin-bottom: 15px; } .bot-bubble { background: linear-gradient(135deg, #e0d4f7 0%, #cbb2fe 100%); padding: 16px 20px; border-radius: 24px 24px 24px 0; max-width: 80%; font-size: 16px; margin-right: auto; margin-bottom: 15px; } </style> """, unsafe_allow_html=True)

Title & Quote

st.markdown('<p class="big-font">💬 WiseBuddy 🧠</p>', unsafe_allow_html=True) st.markdown('<p class="subtitle">Your AI companion for thoughtful advice</p>', unsafe_allow_html=True)

quotes = [ "🌟 Believe you can and you're halfway there.", "🚀 Success is the sum of small efforts repeated daily.", "💡 The best way to predict the future is to create it.", "❤️ You are stronger than you think.", "🔥 Dream big. Start small. Act now." ] st.markdown(f'<div style="text-align:center;padding:10px;border-radius:10px;background:#eee;">{random.choice(quotes)}</div>', unsafe_allow_html=True)

Initialize Chat State

if "chat_state" not in st.session_state: st.session_state.chat_state = { "history": [], "category": "🌟 Motivation & Positivity", "is_processing": False }

Category selection

category = st.selectbox("📝 Choose advice style:", [ "🌟 Motivation & Positivity", "💡 Business & Wealth", "❤️ Love & Relationships", "🧘 Mindfulness & Peace" ], index=0)

if category != st.session_state.chat_state["category"]: st.session_state.chat_state["category"] = category st.session_state.chat_state["history"].append(("bot", f"Switched to {category}. How can I help?"))

Display chat history

st.markdown('<div class="chat-container"><div class="message-area">', unsafe_allow_html=True)

if not st.session_state.chat_state["history"]: st.session_state.chat_state["history"].append(("bot", f"Hello! I'm WiseBuddy in {category} mode. How can I assist you?"))

for speaker, text in st.session_state.chat_state["history"]: if speaker == "user": st.markdown(f'<div class="user-bubble"><strong>You:</strong><br>{text}</div>', unsafe_allow_html=True) else: st.markdown(f'<div class="bot-bubble"><strong>WiseBuddy:</strong><br>{text}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

Input

user_input = st.chat_input("💭 Type your message here...")

if user_input and not st.session_state.chat_state["is_processing"]: st.session_state.chat_state["history"].append(("user", user_input)) st.session_state.chat_state["is_processing"] = True

Process reply

if st.session_state.chat_state["is_processing"]: last_user_message = st.session_state.chat_state["history"][-1][1]

try:
    prompt = f"You are WiseBuddy, specializing in {st.session_state.chat_state['category']}. Be supportive, concise, and positive. Context: {last_user_message}"
    result = model.generate_content(last_user_message)

    st.session_state.chat_state["history"].append(("bot", result.text.strip()))
except Exception:
    st.session_state.chat_state["history"].append(("bot", "⚠️ Oops! Something went wrong. Please try again."))

st.session_state.chat_state["is_processing"] = False

Footer

st.markdown('<div class="footer">WiseBuddy 🧠 • Powered by Gemini</div>', unsafe_allow_html=True)

