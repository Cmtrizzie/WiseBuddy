import streamlit as st
import uuid
import google.generativeai as genai
import hashlib

# --- CONFIG --- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide")

# --- GEMINI SETUP --- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# --- SESSION STATE --- #
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.active_chat = None
if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}

def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_chat = chat_id

def rename_chat(chat_id, new_title):
    st.session_state.chat_sessions[chat_id]["title"] = new_title

def hash_prompt(text):
    return hashlib.sha256(text.encode()).hexdigest()

def generate_reply(user_message):
    prompt = f"{user_message}\n\nRespond clearly, helpfully, and use emojis."
    prompt_hash = hash_prompt(prompt)
    if prompt_hash in st.session_state.response_cache:
        return st.session_state.response_cache[prompt_hash]
    try:
        chat = model.start_chat()
        response = chat.send_message(prompt)
        reply = response.text.strip()
        st.session_state.response_cache[prompt_hash] = reply
        return reply
    except Exception as e:
        if "429" in str(e):
            return "🚫 Quota limit reached. Please try again later."
        return f"⚠️ Gemini error: {e}"

# --- INIT ONE CHAT IF NONE --- #
if not st.session_state.chat_sessions:
    new_chat()

# --- ACTIVE CHAT --- #
active_chat_id = st.session_state.active_chat
active_chat = st.session_state.chat_sessions[active_chat_id]

# --- DARK MODE STYLING --- #
st.markdown("""
<style>
body, .main, .block-container {
    background-color: #000 !important;
    color: #fff !important;
}
.chat-window {
    max-height: calc(100vh - 150px);
    overflow-y: auto;
    padding: 10px 12px 100px 12px;
}
.user-bubble, .bot-bubble {
    display: inline-block;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 16px;
    line-height: 1.4;
    max-width: 75%;
    border-radius: 18px;
}
.user-bubble {
    background-color: #1f1f1f;
    color: #fff;
    float: right;
    clear: both;
}
.bot-bubble {
    background-color: #262626;
    color: #fff;
    float: left;
    clear: both;
}
.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #0d0d0d;
    padding: 12px;
    border-top: 1px solid #222;
    z-index: 1000;
}
.chatbox {
    width: calc(100% - 60px);
    padding: 12px 16px;
    border-radius: 24px;
    border: none;
    background-color: #1f1f1f;
    color: #fff;
    font-size: 16px;
    outline: none;
}
.send-btn {
    display: inline-block;
    width: 40px;
    height: 40px;
    margin-left: 10px;
    background-color: #0055ff;
    border-radius: 50%;
    color: white;
    font-size: 18px;
    border: none;
    text-align: center;
    line-height: 40px;
}
::-webkit-scrollbar {
    width: 4px;
}
::-webkit-scrollbar-thumb {
    background-color: #333;
}
</style>
""", unsafe_allow_html=True)

# --- PAGE TITLE --- #
st.markdown("<h2 style='text-align: center;'>🤖 WiseBuddy</h2>", unsafe_allow_html=True)

# --- WELCOME SCREEN IF EMPTY --- #
if len(active_chat["messages"]) == 0:
    st.markdown("""
        <div style="text-align:center; margin-top: 25vh;">
            <img src="https://emojicdn.elk.sh/🧠" width="80" />
            <h3>Hi, I'm WiseBuddy.</h3>
            <p style="color:#aaa;">How can I help you today?</p>
        </div>
    """, unsafe_allow_html=True)

# --- CHAT HISTORY --- #
st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
for msg in active_chat["messages"]:
    role_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
    st.markdown(f"<div class='{role_class}'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("<div id='scroll-to-bottom'></div></div>", unsafe_allow_html=True)

# --- AUTO SCROLL TO BOTTOM --- #
st.markdown("""
<script>
    const chatEnd = window.parent.document.querySelector('body');
    chatEnd.scrollTo({top: chatEnd.scrollHeight, behavior: 'smooth'});
</script>
""", unsafe_allow_html=True)

# --- CHAT INPUT AREA (FLOATING) --- #
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([11, 1])
    with col1:
        user_input = st.text_input("Message WiseBuddy...", key="chat_input", label_visibility="collapsed", placeholder="Type your message...", help="Press enter or tap plane to send")
    with col2:
        submitted = st.form_submit_button("➤", type="primary")
st.markdown('</div>', unsafe_allow_html=True)

# --- HANDLE SEND --- #
if submitted and user_input.strip():
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    reply = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": reply})

    if len([m for m in active_chat["messages"] if m["role"] == "user"]) == 3:
        rename_chat(active_chat_id, user_input.strip()[:30] + "...")
