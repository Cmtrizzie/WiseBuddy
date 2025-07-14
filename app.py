import streamlit as st
import uuid
import google.generativeai as genai

# --- CONFIG --- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide")

# --- GEMINI API --- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# --- SESSION --- #
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.active_chat = None

def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_chat = chat_id

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

# --- INIT DEFAULT CHAT --- #
if not st.session_state.chat_sessions:
    new_chat()

active_id = st.session_state.active_chat
active_chat = st.session_state.chat_sessions[active_id]

# --- STYLING --- #
st.markdown("""
<style>
body, .main, .block-container {
    background-color: #000 !important;
    color: white !important;
}
.chat-container {
    padding-bottom: 120px;
}
.message {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 20px;
    margin: 10px 0;
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
}
.user {
    background-color: #1e1e1e;
    margin-left: auto;
    text-align: right;
}
.bot {
    background-color: #2b2b2b;
    margin-right: auto;
    text-align: left;
}
.input-box {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #0d0d0d;
    padding: 16px;
    border-top: 1px solid #222;
    z-index: 1000;
}
.input-field {
    display: flex;
    align-items: center;
    background: #1f1f1f;
    border-radius: 30px;
    padding: 10px 14px;
}
input[type="text"] {
    flex-grow: 1;
    background: transparent;
    border: none;
    outline: none;
    color: white;
    font-size: 16px;
}
.send-button {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    font-size: 18px;
    margin-left: 10px;
    cursor: pointer;
}
::-webkit-scrollbar {
    width: 5px;
}
::-webkit-scrollbar-thumb {
    background: #333;
}
</style>
""", unsafe_allow_html=True)

# --- TITLE --- #
st.markdown("<h2 style='text-align: center;'>🤖 WiseBuddy</h2>", unsafe_allow_html=True)

# --- WELCOME --- #
if len(active_chat["messages"]) == 0:
    st.markdown("""
        <div style='text-align: center; margin-top: 25vh;'>
            <img src='https://emojicdn.elk.sh/🤖' width='72'>
            <h3>Hello, I'm WiseBuddy</h3>
            <p style='color: gray;'>How can I assist you today?</p>
        </div>
    """, unsafe_allow_html=True)

# --- MESSAGES --- #
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in active_chat["messages"]:
    role = "user" if msg["role"] == "user" else "bot"
    st.markdown(f"<div class='message {role}'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- INPUT BAR --- #
st.markdown('<div class="input-box">', unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([10, 1])
    with col1:
        user_input = st.text_input("Message", "", label_visibility="collapsed", key="input_text", placeholder="Type your message...")
    with col2:
        send = st.form_submit_button("➤")
st.markdown("</div>", unsafe_allow_html=True)

# --- HANDLE SEND --- #
if send and user_input.strip():
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    response = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": response})

    if len([m for m in active_chat["messages"] if m["role"] == "user"]) == 3:
        rename_chat(active_id, active_chat["messages"][0]["content"][:30] + "...")
