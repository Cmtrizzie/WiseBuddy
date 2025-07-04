import streamlit as st import google.generativeai as genai import random

👉 Configure your Gemini API Key

genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4") model = genai.GenerativeModel('gemini-1.5-flash')

👉 Streamlit Page Setup

st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

👉 Title and Welcome Message

st.markdown("<h1 style='text-align: center;'>💬 WiseBuddy 🧠</h1>", unsafe_allow_html=True) st.markdown("<p style='text-align: center; color: #6c63ff;'>Your AI companion for thoughtful advice</p>", unsafe_allow_html=True)

quotes = [ "🌟 Believe you can and you're halfway there.", "🚀 Success is the sum of small efforts repeated daily.", "💡 The best way to predict the future is to create it.", "❤️ You are stronger than you think.", "🔥 Dream big. Start small. Act now.", "🌱 Growth begins at the end of your comfort zone.", "🌈 After every storm comes a rainbow of possibilities." ]

st.markdown(f""" <div style='background-color:#f0f0ff;padding:10px;border-radius:10px;text-align:center;'> <em>{random.choice(quotes)}</em> </div> """, unsafe_allow_html=True)

👉 Initialize Chat State

if 'history' not in st.session_state: st.session_state.history = [] if 'current_category' not in st.session_state: st.session_state.current_category = "🌟 Motivation & Positivity" if 'chat_session' not in st.session_state: st.session_state.chat_session = model.start_chat(history=[])

👉 Category Selection

category = st.selectbox( "📝 Choose your advice style:", [ "🌟 Motivation & Positivity", "💡 Business & Wealth", "❤️ Love & Relationships", "🧘 Mindfulness & Peace", "🎯 Goal Setting", "🔄 Life Transitions" ], index=[ "🌟 Motivation & Positivity", "💡 Business & Wealth", "❤️ Love & Relationships", "🧘 Mindfulness & Peace", "🎯 Goal Setting", "🔄 Life Transitions" ].index(st.session_state.current_category) )

if category != st.session_state.current_category: st.session_state.current_category = category st.session_state.history.append(("bot", f"Switched to {category}. How can I assist you today?"))

👉 Clear Chat Button

if st.button("🗑️ Clear Chat"): st.session_state.history = [] st.session_state.chat_session = model.start_chat(history=[])

👉 Display Chat History

for speaker, message in st.session_state.history: if speaker == "user": st.markdown(f""" <div style='background-color:#d0f0c0;padding:12px 18px;border-radius:15px;margin-bottom:10px;text-align:right;'> <strong>You:</strong> {message} </div> """, unsafe_allow_html=True) else: st.markdown(f""" <div style='background-color:#e0d4f7;padding:12px 18px;border-radius:15px;margin-bottom:10px;text-align:left;'> <strong>WiseBuddy 🤖:</strong> {message} </div> """, unsafe_allow_html=True)

👉 User Input

user_input = st.chat_input("💭 Type your message here...")

👉 Process Input

if user_input: st.session_state.history.append(("user", user_input))

prompt = f"You are WiseBuddy, an AI advisor in {st.session_state.current_category}. Respond helpfully to: {user_input}"

try:
    response = st.session_state.chat_session.send_message(prompt)
    st.session_state.history.append(("bot", response.text))
except Exception as e:
    st.session_state.history.append(("bot", "⚠️ Sorry, something went wrong. Please try again later."))
    st.error(f"API Error: {e}")

👉 Footer

st.markdown(""" <div style='text-align:center;margin-top:20px;color:#777;'> WiseBuddy 🧠 • Powered by Gemini </div> """, unsafe_allow_html=True)

