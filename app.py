import streamlit as st
import uuid
import google.generativeai as genai
from streamlit.components.v1 import html

# --- CONFIG --- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide", initial_sidebar_state="collapsed")

# --- GEMINI API --- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# --- SESSION --- #
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.active_chat = None
    st.session_state.sidebar_open = False

def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": []
    }
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

/* Hide Streamlit header elements */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarHeader"],
[data-testid="stAppViewContainer"] > header,
.stApp > header {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
}

.block-container {
    padding-top: 0px !important;
    padding-left: 0px !important;
    padding-right: 0px !important;
}

/* Custom Header Styling */
.custom-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background-color: #000000;
    position: sticky;
    top: 0;
    z-index: 1000;
    color: white;
    border-bottom: 1px solid #1a1a1a;
}
.header-item {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px 12px;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.2s ease, color 0.2s ease;
    min-width: 44px;
    min-height: 44px;
    box-sizing: border-box;
}
.header-item:hover {
    background-color: #1a1a1a;
    color: #cccccc;
}
.header-icon {
    font-size: 24px;
}
.header-title {
    font-size: 18px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
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

/* Input bar styling */
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

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0d0d0d;
    color: white;
    padding-top: 10px;
}

[data-testid="stSidebar"] .stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 10px 15px;
    width: 100%;
    margin-bottom: 10px;
    font-size: 16px;
    transition: background-color 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #1a56c7;
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

# --- SIDEBAR CONTENT --- #
with st.sidebar:
    st.markdown("## Chat History")
    if st.button("➕ Start New Chat", key="sidebar_new_chat_button", use_container_width=True):
        new_chat()

    st.markdown("---")

    if st.session_state.chat_sessions:
        sorted_chat_ids = sorted(st.session_state.chat_sessions.keys(),
                                 key=lambda x: st.session_state.chat_sessions[x].get('last_updated', x),
                                 reverse=True)

        for chat_id in sorted_chat_ids:
            chat_data = st.session_state.chat_sessions[chat_id]
            is_active = chat_id == st.session_state.active_chat
            
            if st.button(
                chat_data['title'],
                key=f"sidebar_chat_select_{chat_id}",
                help="Switch to this chat",
                use_container_width=True
            ):
                switch_chat(chat_id)
    else:
        st.markdown("<p style='color: #888;'>No chats yet. Start a new one!</p>")

# --- Custom Header ---
st.markdown(f"""
<div class="custom-header">
    <div class="header-item" id="header-sidebar-toggle" onclick="handleHeaderClick('toggle')">
        <div class="header-icon">☰</div>
    </div>
    <div class="header-item" id="header-chat-title" onclick="handleHeaderClick('title')">
        <div class="header-title">{active_chat["title"]}</div>
    </div>
    <div class="header-item" id="header-new-chat-button" onclick="handleHeaderClick('new')">
        <div class="header-icon">+</div>
    </div>
</div>
""", unsafe_allow_html=True)

# JavaScript for header interactivity
html("""
<script>
function handleHeaderClick(action) {
    if (action === 'toggle') {
        // Toggle sidebar
        const sidebarToggleButton = window.parent.document.querySelector('[data-testid="stSidebarToggleButton"]');
        if (sidebarToggleButton) sidebarToggleButton.click();
    } 
    else if (action === 'new') {
        // Create new chat
        const newChatEvent = new CustomEvent('newChatRequested', { detail: {} });
        window.dispatchEvent(newChatEvent);
    }
    else if (action === 'title') {
        // Chat title click
        const titleClickEvent = new CustomEvent('chatTitleClicked', { detail: {} });
        window.dispatchEvent(titleClickEvent);
    }
}

// Listen for events
window.addEventListener('newChatRequested', function() {
    window.parent.postMessage({type: 'NEW_CHAT_REQUEST'}, '*');
});

window.addEventListener('chatTitleClicked', function() {
    window.parent.postMessage({type: 'CHAT_TITLE_CLICK'}, '*');
});
</script>
""")

# --- Handle header events ---
if 'header_events' not in st.session_state:
    st.session_state.header_events = {'new': False, 'title': False}

# Listen for new chat requests
if st.session_state.header_events['new']:
    new_chat()
    st.session_state.header_events['new'] = False

# Listen for title clicks
if st.session_state.header_events['title']:
    st.toast(f"You clicked on: '{active_chat['title']}'", icon="ℹ️")
    st.session_state.header_events['title'] = False

# Listen for messages from JavaScript
html("""
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "NEW_CHAT_REQUEST") {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'NEW_CHAT_REQUEST'}, '*');
    }
    else if (event.data.type === "CHAT_TITLE_CLICK") {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'CHAT_TITLE_CLICK'}, '*');
    }
});
</script>
""")

# Update state based on messages
if 'NEW_CHAT_REQUEST' in st.session_state:
    st.session_state.header_events['new'] = True
    del st.session_state['NEW_CHAT_REQUEST']
    
if 'CHAT_TITLE_CLICK' in st.session_state:
    st.session_state.header_events['title'] = True
    del st.session_state['CHAT_TITLE_CLICK']

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
