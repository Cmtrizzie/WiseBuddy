import streamlit as st
import random
import uuid
import datetime
import re

# --- Initialize Session State for Multiple Chats ---
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    st.session_state['active_chat'] = None
    st.session_state['search_query'] = ""
    st.session_state['pre_fill_input'] = ""
    st.session_state['tagged_chats'] = {}
    st.session_state['archived_chats_visible'] = False
    st.session_state['current_input'] = ""

# --- Helper Functions for Chat Management ---
def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state['chat_sessions'][chat_id] = {
        'title': f'New Chat {len(st.session_state["chat_sessions"]) + 1}',
        'messages': [],
        'timestamp': datetime.datetime.now().isoformat(),
        'archived': False,
        'tagged': False
    }
    st.session_state['active_chat'] = chat_id
    st.session_state['pre_fill_input'] = ""
    st.session_state['current_input'] = ""

def generate_chat_title(user_input):
    """Generate a meaningful title from user input"""
    first_sentence = re.split(r'[.!?]', user_input)[0].strip()
    words = first_sentence.split()[:5]
    return ' '.join(words) + ("..." if len(first_sentence) > 15 else "")

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="WiseBuddy Chat")

# --- Enhanced CSS for ChatGPT-like Styling ---
st.markdown("""
<style>
    :root {
        --sidebar-bg: #202123;
        --main-bg: #343541;
        --input-bg: #40414f;
        --border-color: #444654;
        --text-primary: #ececf1;
        --text-secondary: #8e8ea0;
        --accent: #10a37f;
        --user-bubble: #007bff;
        --bot-bubble: #444654;
    }
    
    html, body, .stApp {
        margin: 0;
        padding: 0;
        height: 100%;
        background-color: var(--main-bg);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
    }
    
    .stApp {
        display: flex;
        flex-direction: row;
        height: 100vh;
    }

    /* Sidebar Styling */
    .stSidebar {
        width: 260px !important;
        background-color: var(--sidebar-bg);
        padding-top: 10px;
        display: flex;
        flex-direction: column;
    }
    
    .sidebar-header {
        padding: 0 15px 10px 15px;
    }
    
    .new-chat-btn {
        background-color: var(--main-bg);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        width: 100%;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: normal;
        transition: background-color 0.2s ease;
        text-align: center;
        cursor: pointer;
    }
    
    .new-chat-btn:hover {
        background-color: var(--border-color);
    }
    
    .sidebar-search {
        padding: 10px 15px 5px 15px;
    }
    
    .sidebar-search input {
        background-color: var(--main-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 5px !important;
        padding: 8px 12px !important;
        width: 100%;
    }
    
    .section-title {
        padding: 10px 15px 5px 15px;
        color: var(--text-secondary);
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .sidebar-chat-list {
        flex-grow: 1;
        overflow-y: auto;
        padding: 0 15px;
    }
    
    .sidebar-chat-item {
        background-color: var(--main-bg);
        color: var(--text-primary);
        border: none;
        padding: 8px 12px;
        margin-bottom: 4px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s ease;
        display: flex;
        align-items: center;
        font-size: 0.9em;
        position: relative;
    }
    
    .sidebar-chat-item:hover {
        background-color: var(--border-color);
    }
    
    .sidebar-chat-item.active-chat {
        background-color: var(--border-color);
    }
    
    .chat-item-title {
        flex-grow: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-right: 25px;
    }
    
    .chat-status-icon {
        position: absolute;
        right: 10px;
        font-size: 0.9em;
    }
    
    .sidebar-footer {
        padding: 15px;
        border-top: 1px solid var(--border-color);
        color: var(--text-secondary);
        font-size: 0.9em;
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .user-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    
    /* Main Content Area */
    .main-header {
        background-color: var(--main-bg);
        padding: 12px 20px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .chat-title-display {
        font-size: 1.1em;
        font-weight: 500;
    }
    
    .get-plus-btn {
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 8px 15px !important;
        border-radius: 20px !important;
        font-weight: bold !important;
    }
    
    .chat-messages-container {
        flex-grow: 1;
        overflow-y: auto;
        padding: 20px;
        padding-bottom: 100px;
        display: flex;
        flex-direction: column;
    }
    
    .message-row {
        display: flex;
        width: 100%;
        max-width: 800px;
        margin: 0 auto 12px auto;
    }
    
    .user-bubble, .bot-bubble {
        max-width: 85%;
        padding: 12px 16px;
        border-radius: 18px;
        word-wrap: break-word;
        font-size: 0.95em;
        line-height: 1.5;
    }
    
    .user-bubble {
        background-color: var(--user-bubble);
        margin-left: auto;
    }
    
    .bot-bubble {
        background-color: var(--bot-bubble);
        margin-right: auto;
    }
    
    /* Welcome Screen */
    .welcome-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
        padding: 20px;
        text-align: center;
        color: var(--text-secondary);
        max-width: 700px;
        margin: 0 auto;
    }
    
    .welcome-title {
        font-size: 2em;
        margin-bottom: 30px;
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .suggestion-list {
        display: flex;
        flex-direction: column;
        gap: 15px;
        width: 100%;
        text-align: left;
    }
    
    .suggestion-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 15px;
        background-color: var(--bot-bubble);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    
    .suggestion-item:hover {
        background-color: var(--border-color);
    }
    
    .suggestion-icon {
        font-size: 1.2em;
    }
    
    /* Input Area */
    .input-area-container {
        position: fixed;
        bottom: 0;
        left: 260px;
        right: 0;
        background: var(--main-bg);
        padding: 15px 0;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: center;
    }
    
    .input-wrapper {
        width: 100%;
        max-width: 700px;
        padding: 0 20px;
    }
    
    .input-group {
        display: flex;
        align-items: center;
        background-color: var(--input-bg);
        border-radius: 25px;
        padding: 5px 15px;
    }
    
    .input-group .stTextInput > div > div > input {
        background: transparent !important;
        color: var(--text-primary) !important;
        border: none !important;
        padding: 12px 5px !important;
        font-size: 1em !important;
        box-shadow: none !important;
    }
    
    .input-group .stTextInput > div > div > input::placeholder {
        color: var(--text-secondary) !important;
    }
    
    .input-icon-btn {
        background: none !important;
        border: none !important;
        color: var(--text-secondary) !important;
        font-size: 1.4em !important;
        padding: 8px 10px !important;
    }
    
    .send-btn {
        color: var(--accent) !important;
        font-size: 1.6em !important;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu, header, footer, .stDeployButton {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chats if needed
if not st.session_state.get('chat_sessions'):
    new_chat()

# --- Sidebar (Chat Navigation and Management) ---
with st.sidebar:
    # New Chat button
    st.markdown("<div class='sidebar-header'>", unsafe_allow_html=True)
    st.markdown("<div class='new-chat-btn'>+ New chat</div>", unsafe_allow_html=True)
    st.markdown("</div>")

    # Search functionality
    st.markdown("<div class='sidebar-search'>", unsafe_allow_html=True)
    st.session_state['search_query'] = st.text_input(
        "",
        value=st.session_state['search_query'],
        placeholder="Search chats...",
        key="chat_search_input",
        label_visibility="collapsed"
    )
    st.markdown("</div>")

    # Chats section
    st.markdown("<div class='section-title'>CHATS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-chat-list'>", unsafe_allow_html=True)

    # Display active chats
    for chat_id, chat_data in st.session_state['chat_sessions'].items():
        if not chat_data['archived']:
            is_active = (chat_id == st.session_state['active_chat'])
            st.markdown(f"""
                <div class='sidebar-chat-item {"active-chat" if is_active else ""}'>
                    <div class='chat-item-title'>{chat_data['title']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Hidden button to switch chats
            if st.button("", key=f"select_chat_{chat_id}"):
                st.session_state['active_chat'] = chat_id
                st.session_state['current_input'] = ""
                st.experimental_rerun()

    # Archive toggle
    st.markdown("<div style='padding: 10px 0;'>", unsafe_allow_html=True)
    if st.button("🗄️ Show Archived Chats" if not st.session_state['archived_chats_visible'] else "🗄️ Hide Archived Chats"):
        st.session_state['archived_chats_visible'] = not st.session_state['archived_chats_visible']
        st.experimental_rerun()
    st.markdown("</div>")

    # Archived chats section
    if st.session_state['archived_chats_visible']:
        archived_exists = False
        for chat_id, chat_data in st.session_state['chat_sessions'].items():
            if chat_data['archived']:
                if not archived_exists:
                    st.markdown("<div class='section-title'>ARCHIVED CHATS</div>", unsafe_allow_html=True)
                    archived_exists = True
                
                st.markdown(f"""
                    <div class='sidebar-chat-item'>
                        <div class='chat-item-title'>{chat_data['title']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("", key=f"select_archived_{chat_id}"):
                    st.session_state['active_chat'] = chat_id
                    st.session_state['current_input'] = ""
                    st.experimental_rerun()

    st.markdown("</div>")  # End sidebar-chat-list

    # Sidebar Footer
    st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
    st.markdown("<div class='user-profile'>", unsafe_allow_html=True)
    st.markdown("<div class='user-avatar'>M</div>", unsafe_allow_html=True)
    st.markdown("<div><strong>Mark Comrade</strong><br>Free Plan</div>", unsafe_allow_html=True)
    st.markdown("</div>")
    st.markdown("</div>")

# --- Main Chat Area ---
active_chat_id = st.session_state['active_chat']
if active_chat_id in st.session_state['chat_sessions']:
    active_chat_data = st.session_state['chat_sessions'][active_chat_id]
else:
    # Create new chat if active chat doesn't exist
    new_chat()
    active_chat_id = st.session_state['active_chat']
    active_chat_data = st.session_state['chat_sessions'][active_chat_id]

# Main Header
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.markdown(f"<div class='chat-title-display'>{active_chat_data['title']}</div>", unsafe_allow_html=True)
st.button("✨ Get Plus", key="get_plus_btn", help="Upgrade to Plus for advanced features")
st.markdown("</div>")

# Chat messages display area
st.markdown("<div class='chat-messages-container'>", unsafe_allow_html=True)

if not active_chat_data['messages']:
    # Welcome screen - using list items instead of buttons
    st.markdown("<div class='welcome-screen'>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-title'>What can I help with?</div>", unsafe_allow_html=True)
    st.markdown("<div class='suggestion-list'>", unsafe_allow_html=True)
    
    # Suggestion items as list
    suggestions = [
        ("🖼️", "Create image"),
        ("💡", "Make a plan"),
        ("📄", "Summarize text"),
        ("➕", "More")
    ]
    
    for icon, text in suggestions:
        st.markdown(f"""
            <div class='suggestion-item' onclick='document.querySelector("[key=\\'suggest_{text.replace(" ", "_")}\\']").click()'>
                <div class='suggestion-icon'>{icon}</div>
                <div>{text}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Hidden button for each suggestion
        if st.button(f"suggest_{text}", key=f"suggest_{text.replace(' ', '_')}", visible=False):
            st.session_state['pre_fill_input'] = f"{text}: "
            st.experimental_rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)
else:
    # Display actual messages
    for msg in active_chat_data['messages']:
        if msg['role'] == 'user':
            st.markdown(f"<div class='message-row'><div class='user-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message-row'><div class='bot-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

st.markdown("</div>")  # End chat-messages-container

# --- Input Area ---
st.markdown("<div class='input-area-container'>", unsafe_allow_html=True)
st.markdown("<div class='input-wrapper'>", unsafe_allow_html=True)
st.markdown("<div class='input-group'>", unsafe_allow_html=True)

# Initialize input value
input_value = st.session_state.get('pre_fill_input', '') or st.session_state.get('current_input', '')

# Create columns for layout
col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col1:
    # Attachment button
    if st.button("📎", key="attach_btn", help="Attach files"):
        st.toast("File attachment feature coming soon!")

with col2:
    # Text input field
    user_input = st.text_input(
        "",
        value=input_value,
        placeholder="Message WiseBuddy...",
        key='user_input_field',
        label_visibility="collapsed"
    )
    # Update current input state
    st.session_state['current_input'] = user_input
    
    # Clear pre-fill after use
    if st.session_state.get('pre_fill_input'):
        st.session_state['pre_fill_input'] = ""

with col3:
    # Send button
    send_clicked = st.button("⬆️", key="send_btn", help="Send message")

st.markdown("</div>", unsafe_allow_html=True)  # End input-group
st.markdown("</div>", unsafe_allow_html=True)  # End input-wrapper
st.markdown("</div>", unsafe_allow_html=True)  # End input-area-container

# Handle message submission
if send_clicked and st.session_state['current_input'].strip():
    user_input = st.session_state['current_input'].strip()
    
    # Add user message
    active_chat_data['messages'].append({'role': 'user', 'content': user_input})
    
    # Auto-generate title if it's a new chat
    if active_chat_data['title'].startswith('New Chat'):
        active_chat_data['title'] = generate_chat_title(user_input)
    
    # Simulate AI response
    responses = [
        "I understand your question about **{}**. Here's what I can tell you...",
        "Great question! Regarding **{}**, here's the information you need:",
        "Based on your query about **{}**, here's a detailed response:"
    ]
    
    # Extract first keyword from user input
    keywords = re.findall(r'\b(\w{4,})\b', user_input)
    keyword = keywords[0] if keywords else "your query"
    
    ai_response = random.choice(responses).format(keyword)
    active_chat_data['messages'].append({'role': 'assistant', 'content': ai_response})
    
    # Clear input after submission
    st.session_state['current_input'] = ""
    st.session_state['pre_fill_input'] = ""
    
    st.experimental_rerun()
