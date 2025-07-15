# ✅ FINAL STREAMLIT CODE FOR WISEBUDDY WITH GEMINI INTEGRATION + CUSTOM UI

import streamlit as st
import uuid
import google.generativeai as genai

# ---------------- CONFIG ----------------
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide", initial_sidebar_state="collapsed")

# ---------------- GEMINI API ----------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# ---------------- SESSION INIT ----------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.active_chat = None
if "new_chat_clicked" not in st.session_state:
    st.session_state.new_chat_clicked = False

# ---------------- CHAT HELPERS ----------------
def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_sessions[chat_id] = {"title": "New Chat", "messages": []}
    st.session_state.active_chat = chat_id
    st.rerun()

def switch_chat(chat_id):
    st.session_state.active_chat = chat_id
    st.rerun()

def rename_chat(chat_id, title):
    st.session_state.chat_sessions[chat_id]["title"] = title

def generate_reply(user_input):
    try:
        chat = model.start_chat()
        response = chat.send_message(user_input)
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):
            return "🚫 API quota limit reached. Please wait a bit and try again!"
        return f"⚠️ Gemini error: {str(e)}"

# ---------------- INIT DEFAULT CHAT ----------------
if not st.session_state.chat_sessions:
    new_chat()

active_id = st.session_state.active_chat
active_chat = st.session_state.chat_sessions[active_id]

# ---------------- STYLING ----------------
st.markdown(open("styles.css").read(), unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## Chat History")
    if st.button("➕ Start New Chat", key="sidebar_new_chat_button"):
        new_chat()
    st.markdown("---")

    if st.session_state.chat_sessions:
        for chat_id, chat_data in st.session_state.chat_sessions.items():
            if st.button(chat_data['title'], key=f"switch_chat_{chat_id}"):
                switch_chat(chat_id)
    else:
        st.markdown("<p style='color: #888;'>No chats yet. Start a new one!</p>", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(f"""
<div class="custom-header">  
    <div class="header-item" onclick="window.parent.document.querySelector('[data-testid=\"stSidebar\"] button').click()">☰</div>  
    <div class="header-item header-title">{active_chat['title']}</div>  
    <div class="header-item" onclick="window.parent.location.reload()">+</div>  
</div>
""", unsafe_allow_html=True)

# ---------------- WELCOME OR CHAT ----------------
if len(active_chat["messages"]) == 0:
    st.markdown("""
    <div class='welcome-message'>
        <img src='https://emojicdn.elk.sh/🤖' width='72'>
        <h3>Hello, I'm WiseBuddy</h3>
        <p>How can I assist you today?</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in active_chat["messages"]:
        role = "user" if msg["role"] == "user" else "bot"
        st.markdown(f"<div class='message {role}'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Type your message...")

if user_input:
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    response = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": response})

    user_msg_count = len([m for m in active_chat["messages"] if m["role"] == "user"])
    if user_msg_count == 3 and active_chat["title"] == "New Chat":
        rename_chat(active_id, active_chat["messages"][0]["content"][:30].strip() + "...")

    st.rerun()
```
