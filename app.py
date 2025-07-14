import streamlit as st
import uuid
import google.generativeai as genai
import hashlib

# ---- CONFIG ---- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide")

# ---- GEMINI API ---- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# ---- SESSION STATE ---- #
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

def generate_reply_with_gemini(user_message):
    prompt = f"{user_message}\n\nRespond helpfully and clearly. Use emojis where appropriate!"
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
        err = str(e)
        if "429" in err or "quota" in err.lower():
            return "🚫 API quota limit reached. Please wait a bit and try again!"
        return f"⚠️ Gemini error: {err}"

# ---- INIT ONE CHAT ---- #
if not st.session_state.chat_sessions:
    new_chat()

# ---- SIDEBAR ---- #
with st.sidebar:
    st.title("💬 Chats")
    if st.button("➕ New Chat", key="create_new"):
        new_chat()
    for chat_id, chat in st.session_state.chat_sessions.items():
        if st.button(chat["title"], key=f"chat_{chat_id}"):
            st.session_state.active_chat = chat_id

# ---- ACTIVE CHAT ---- #
active_chat_id = st.session_state.active_chat
active_chat = st.session_state.chat_sessions[active_chat_id]

# ---- CUSTOM STYLING ---- #
st.markdown("""
    <style>
        .main-title {
            font-size: 42px;
            font-weight: bold;
            margin-top: -5px;
            margin-bottom: 15px;
        }
        .chat-window {
            max-height: calc(100vh - 140px);
            overflow-y: auto;
            padding-right: 10px;
            padding-bottom: 110px;
        }
        .chat-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 12px 1rem;
            background: white;
            border-top: 1px solid #eee;
            z-index: 999;
            max-width: 720px;
            margin: 0 auto;
        }
        input.chatbox {
            width: 100%;
            padding: 10px 16px;
            font-size: 16px;
            border-radius: 25px;
            border: 1px solid #ccc;
            background: white !important;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# ---- TITLE ---- #
st.markdown("<div class='main-title'>🤖 WiseBuddy</div>", unsafe_allow_html=True)

# ---- CHAT DISPLAY ---- #
st.markdown("<div class='chat-window'>", unsafe_allow_html=True)

bubble_style = """display:inline-block;padding:10px 15px;border-radius:15px;
                  margin:6px 0;max-width:75%;font-size:16px;line-height:1.5;
                  box-shadow:0 1px 3px rgba(0,0,0,0.1);"""

for msg in active_chat["messages"]:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='{bubble_style} background:#dcf8c6; color:#000; float:right; clear:both;'>{msg['content']}</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='{bubble_style} background:#f1f0f0; color:#000; float:left; clear:both;'>{msg['content']}</div>",
            unsafe_allow_html=True)

# ---- AUTO-SCROLL TARGET ---- #
st.markdown("<div id='scroll-to-bottom'></div>", unsafe_allow_html=True)
st.markdown("""
    <script>
        const chatBox = window.parent.document.querySelector('body');
        chatBox.scrollTo({top: chatBox.scrollHeight, behavior: 'smooth'});
    </script>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---- FIXED INPUT FIELD ---- #
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([10, 1])
    with col1:
        user_input = st.text_input("Type a message...", key="input_message", label_visibility="collapsed")
    with col2:
        submitted = st.form_submit_button("🛩️", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---- ON SEND ---- #
if submitted and user_input.strip():
    active_chat["messages"].append({'role': 'user', 'content': user_input.strip()})
    reply = generate_reply_with_gemini(user_input.strip())
    active_chat["messages"].append({'role': 'assistant', 'content': reply})

    user_msgs = [m for m in active_chat["messages"] if m["role"] == "user"]
    if len(user_msgs) == 3:
        rename_chat(active_chat_id, user_msgs[0]["content"][:30] + "...")
