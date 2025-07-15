import streamlit as st
import uuid
import google.generativeai as genai

# --- CONFIG --- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide", initial_sidebar_state="collapsed")

# --- GEMINI API --- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# --- SESSION --- #
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.active_chat = None
if "slidebar_position" not in st.session_state:
    st.session_state.slidebar_position = "right"
if "slidebar_open" not in st.session_state:
    st.session_state.slidebar_open = False

def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_chat = chat_id
    st.session_state.slidebar_open = False
    st.rerun()

def switch_chat(chat_id):
    st.session_state.active_chat = chat_id
    st.session_state.slidebar_open = False
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

def toggle_slidebar():
    st.session_state.slidebar_open = not st.session_state.slidebar_open
    st.rerun()

def swap_slidebar_position():
    st.session_state.slidebar_position = "left" if st.session_state.slidebar_position == "right" else "right"
    st.rerun()

# --- INIT DEFAULT CHAT --- #
if not st.session_state.chat_sessions:
    new_chat()

active_id = st.session_state.active_chat
active_chat = st.session_state.chat_sessions[active_id]

# --- STYLING --- #
st.markdown("""
<style>
/* Base styling */
body, .main, .block-container, [data-testid="stAppViewContainer"] {
    background-color: #000000 !important;
    color: white !important;
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit elements */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarHeader"],
[data-testid="stAppViewContainer"] > header,
.stApp > header {
    display: none !important;
}

.block-container {
    padding-top: 0px !important;
    padding-left: 0px !important;
    padding-right: 0px !important;
}

/* Custom Header */
.custom-header {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    background-color: #000000;
    position: sticky;
    top: 0;
    z-index: 1000;
    color: white;
    border-bottom: 1px solid #1a1a1a;
}
.header-title {
    font-size: 18px;
    font-weight: 500;
    text-align: center;
    width: 100%;
}

/* Chat Message Container */
.chat-container {
    padding-bottom: 120px;
    padding-top: 20px;
    max-width: 800px;
    margin: 0 auto;
    padding-left: 15px;
    padding-right: 15px;
}
.message {
    max-width: 75%;
    padding: 12px 18px;
    border-radius: 22px;
    margin: 10px 0;
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.user {
    background-color: #1a1a1a;
    margin-left: auto;
    text-align: right;
    border-bottom-right-radius: 8px;
}
.bot {
    background-color: #282828;
    margin-right: auto;
    text-align: left;
    border-bottom-left-radius: 8px;
}

/* Welcome Message */
.welcome-message {
    text-align: center;
    margin-top: 25vh;
    color: gray;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 20px;
}
.welcome-message img {
    filter: drop-shadow(0 0 10px rgba(0, 150, 255, 0.4));
}
.welcome-message h3 {
    color: white;
    margin-top: 15px;
    margin-bottom: 5px;
    font-size: 26px;
}
.welcome-message p {
    font-size: 17px;
    color: #aaaaaa;
}

/* Input bar */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #000000;
    padding: 15px 20px;
    border-top: 1px solid #1a1a1a;
    z-index: 1000;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}
[data-testid="stChatInput"] > div > label + div {
    background: #1f1f1f;
    border-radius: 30px;
    border: 1px solid #333333;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
    max-width: 760px;
    width: 100%;
    padding: 0;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: white !important;
    font-size: 16px !important;
    padding: 12px 15px !important;
    line-height: 1.5 !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #888 !important;
}
[data-testid="stChatInput"] button {
    background-color: #2563eb !important;
    color: white !important;
    border: none !important;
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    font-size: 20px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin-left: 8px !important;
    padding: 0 !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease, transform 0.1s ease !important;
    flex-shrink: 0 !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.4) !important;
}

/* Slidebar styles */
.slidebar-container {
    position: fixed;
    top: 0;
    width: 300px;
    height: 100vh;
    background-color: #0d0d0d;
    z-index: 999;
    transition: transform 0.3s ease;
    padding-top: 60px;
    overflow-y: auto;
}
.slidebar-left {
    left: 0;
    transform: translateX(-100%);
}
.slidebar-right {
    right: 0;
    transform: translateX(100%);
}
.slidebar-open {
    transform: translateX(0) !important;
}
.slidebar-toggle {
    position: fixed;
    top: 15px;
    z-index: 1000;
    background: #2563eb;
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0,0,0,0.4);
}
.toggle-left {
    left: 15px;
}
.toggle-right {
    right: 15px;
}
.slidebar-content {
    padding: 20px;
}
.slidebar-content button {
    width: 100%;
    margin-bottom: 15px;
    background-color: #2563eb;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 8px;
    cursor: pointer;
}
.sidebar-chat-item-container {
    margin-bottom: 5px;
}
.sidebar-chat-item {
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    word-wrap: break-word;
    color: white;
}
.sidebar-chat-item:hover {
    background-color: #1a1a1a;
}
.sidebar-chat-item.active {
    background-color: #282828;
    border-left: 3px solid #2563eb;
    padding-left: 12px;
}
</style>
""", unsafe_allow_html=True)

# --- Custom Header HTML ---
st.markdown(f"""
<div class="custom-header">
    <div class="header-title">{active_chat["title"]}</div>
</div>
""", unsafe_allow_html=True)

# --- SLIDEBAR TOGGLE BUTTON --- #
toggle_position = "toggle-left" if st.session_state.slidebar_position == "left" else "toggle-right"
st.markdown(f"""
<div class="slidebar-toggle {toggle_position}" id="slidebar-toggle-button">
    ☰
</div>
""", unsafe_allow_html=True)

# --- SLIDEBAR CONTENT --- #
slidebar_class = f"slidebar-{st.session_state.slidebar_position}"
if st.session_state.slidebar_open:
    slidebar_class += " slidebar-open"

with st.container():
    st.markdown(f"""
    <div class="slidebar-container {slidebar_class}">
        <div class="slidebar-content">
            <h3 style="color: white; margin-bottom: 20px;">Chat History</h3>
    """, unsafe_allow_html=True)
    
    if st.button("Swap Side (←→)", key="swap_side_button"):
        swap_slidebar_position()
    
    if st.button("➕ Start New Chat", key="new_chat_button"):
        new_chat()
    
    st.markdown("<div class='sidebar-chat-list'>", unsafe_allow_html=True)
    
    if st.session_state.chat_sessions:
        sorted_chat_ids = sorted(st.session_state.chat_sessions.keys())
        for chat_id in sorted_chat_ids:
            chat_data = st.session_state.chat_sessions[chat_id]
            is_active = "active" if chat_id == st.session_state.active_chat else ""
            if st.button(
                chat_data['title'],
                key=f"chat_{chat_id}",
                help=f"Switch to {chat_data['title']}"
            ):
                switch_chat(chat_id)
    else:
        st.markdown("<p style='color: #888;'>No chats yet. Start a new one!</p>", unsafe_allow_html=True)
    
    st.markdown("</div></div></div>", unsafe_allow_html=True)

# JavaScript for toggle button
components.html(f"""
<script>
document.getElementById('slidebar-toggle-button').addEventListener('click', function() {{
    window.parent.document.dispatchEvent(new CustomEvent('TOGGLE_SLIDEBAR'));
}});
</script>
""", height=0)

# --- WELCOME MESSAGE / CHAT MESSAGES --- #
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

# --- ST.CHAT_INPUT FOR MESSAGING --- #
user_input = st.chat_input("Type your message...")

# --- HANDLE SEND --- #
if user_input:
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    response = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": response})

    active_chat['last_updated'] = str(uuid.uuid4())

    user_message_count = len([m for m in active_chat["messages"] if m["role"] == "user"])
    if user_message_count == 3 and active_chat["title"] == "New Chat":
        rename_chat(active_id, active_chat["messages"][0]["content"][:30].strip() + "...")

    st.rerun()
