import streamlit as st
import random
import uuid
import datetime # For potential timestamping later

# --- Initialize Session State for Multiple Chats ---
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    st.session_state['active_chat'] = None
    st.session_state['search_query'] = "" # For sidebar search
    st.session_state['show_rename_input'] = {} # To control rename input visibility

# --- Helper Functions for Chat Management ---

def new_chat():
    """Creates a new chat session and sets it as active."""
    chat_id = str(uuid.uuid4())
    st.session_state['chat_sessions'][chat_id] = {
        'title': f'New Chat {len(st.session_state["chat_sessions"]) + 1}',
        'messages': [],
        'timestamp': datetime.datetime.now().isoformat(), # Add timestamp
        'archived': False # New field for archiving
    }
    st.session_state['active_chat'] = chat_id
    st.session_state['show_rename_input'] = {} # Reset rename input visibility

def rename_chat(chat_id, new_title):
    """Renames a chat session."""
    if chat_id in st.session_state['chat_sessions']:
        st.session_state['chat_sessions'][chat_id]['title'] = new_title
        st.session_state['show_rename_input'][chat_id] = False # Hide input after rename
        st.experimental_rerun() # Rerun to update sidebar title

def delete_chat(chat_id):
    """Deletes a chat session."""
    if chat_id in st.session_state['chat_sessions']:
        del st.session_state['chat_sessions'][chat_id]
        if st.session_state['active_chat'] == chat_id:
            # If deleting active chat, switch to another or create new
            available_chats = [cid for cid, chat_data in st.session_state['chat_sessions'].items() if not chat_data['archived']]
            if available_chats:
                st.session_state['active_chat'] = available_chats[0] # Just pick the first available
            else:
                new_chat() # No chats left, create a new one
        st.experimental_rerun()

def archive_chat(chat_id):
    """Archives a chat session (placeholder logic)."""
    if chat_id in st.session_state['chat_sessions']:
        st.session_state['chat_sessions'][chat_id]['archived'] = True
        # If archiving active chat, switch to another
        if st.session_state['active_chat'] == chat_id:
            available_chats = [cid for cid, chat_data in st.session_state['chat_sessions'].items() if not chat_data['archived']]
            if available_chats:
                st.session_state['active_chat'] = available_chats[0]
            else:
                new_chat() # All chats archived, start a new one
        st.experimental_rerun() # Rerun to update sidebar

def ensure_chat_exists():
    """Ensures there's always at least one chat session and an active chat."""
    if not st.session_state['chat_sessions']:
        new_chat()
    if st.session_state['active_chat'] not in st.session_state['chat_sessions']:
        # Try to find an unarchived chat
        unarchived_chats = [cid for cid, chat_data in st.session_state['chat_sessions'].items() if not chat_data['archived']]
        if unarchived_chats:
            st.session_state['active_chat'] = unarchived_chats[0]
        else:
            new_chat() # If all are archived, create new one

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="WiseBuddy Chat")

# --- Custom CSS for ChatGPT-like Styling ---
# We'll use a lot of CSS to override Streamlit's defaults and achieve the desired look
st.markdown("""
<style>
    /* General layout adjustments for full height and flexbox */
    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        overflow: hidden; /* Prevent body scroll */
    }
    .stApp {
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: row; /* Sidebar and main content side-by-side */
        height: 100vh; /* Full viewport height */
        background-color: #343541; /* Dark background for main chat area */
    }

    /* Sidebar specific styling */
    .stSidebar {
        width: 260px !important; /* Fixed width for sidebar */
        min-width: 260px !important;
        max-width: 260px !important;
        background-color: #202123; /* Darker background for sidebar */
        color: #ececf1;
        padding-top: 20px;
        box-shadow: 2px 0 5px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
    }
    .stSidebar > div:first-child { /* Target the inner div containing sidebar content */
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    .sidebar-header {
        padding: 0 15px 15px 15px;
        color: #ececf1;
    }
    .sidebar-header h2 {
        margin-bottom: 10px;
        font-size: 1.2em;
    }
    .sidebar-header .stButton button {
        background-color: #343541;
        color: #ececf1;
        border: 1px solid #444654;
        width: 100%;
        text-align: left;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: normal;
        transition: background-color 0.2s ease;
    }
    .sidebar-header .stButton button:hover {
        background-color: #444654;
    }
    .sidebar-chat-list {
        flex-grow: 1; /* Makes the chat list take up available space */
        overflow-y: auto; /* Scroll for chat list */
        padding: 0 15px;
        margin-top: 10px;
    }
    .sidebar-chat-item {
        background-color: #343541;
        color: #ececf1;
        border: none;
        padding: 10px 15px;
        margin-bottom: 5px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.9em;
    }
    .sidebar-chat-item:hover {
        background-color: #444654;
    }
    .sidebar-chat-item.active-chat {
        background-color: #444654;
        font-weight: bold;
    }
    .chat-item-title {
        flex-grow: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-right: 10px; /* Space for buttons */
    }
    .chat-item-actions {
        display: flex;
        gap: 5px;
    }
    .chat-item-actions button {
        background: none !important;
        border: none !important;
        color: #8e8ea0 !important;
        font-size: 0.8em !important;
        padding: 5px !important;
        margin: 0 !important;
        line-height: 1 !important;
        min-height: unset !important;
        width: auto !important; /* Ensure buttons are not full width */
    }
    .chat-item-actions button:hover {
        color: #ececf1 !important;
        background-color: #555 !important;
    }
    .sidebar-footer {
        padding: 15px;
        border-top: 1px solid #3e3f4b;
        color: #8e8ea0;
        font-size: 0.9em;
    }
    .sidebar-footer .stButton button {
        background-color: #343541;
        color: #ececf1;
        border: none;
        width: 100%;
        text-align: left;
        padding: 10px 15px;
        border-radius: 5px;
        transition: background-color 0.2s ease;
    }
    .sidebar-footer .stButton button:hover {
        background-color: #444654;
    }


    /* Main content area */
    .css-1d391kg { /* Target Streamlit's main content div */
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        height: 100vh;
        overflow: hidden; /* Important to manage internal scrolling */
        background-color: #343541; /* Dark background */
        color: #ececf1;
    }

    /* Top header in main content area */
    .main-header {
        background-color: #343541; /* Match main background */
        padding: 10px 20px;
        border-bottom: 1px solid #444654;
        display: flex;
        justify-content: space-between;
        align-items: center;
        min-height: 50px;
    }
    .main-header .stButton button {
        background-color: #10a37f; /* ChatGPT green for Plus */
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        transition: background-color 0.2s ease;
    }
    .main-header .stButton button:hover {
        background-color: #0d8a6e;
    }
    .chat-title-display {
        font-size: 1.1em;
        font-weight: bold;
        color: #ececf1;
    }


    /* Chat messages container */
    .chat-messages-container {
        flex-grow: 1; /* Takes up available space */
        overflow-y: auto; /* Scroll for messages */
        padding: 20px;
        padding-bottom: 100px; /* Space for fixed input area */
        display: flex;
        flex-direction: column;
        align-items: center; /* Center bubbles */
    }
    .message-row {
        display: flex;
        width: 100%;
        justify-content: center; /* Center the message bubbles */
    }
    .user-bubble, .bot-bubble {
        max-width: 65%; /* Max width for message bubbles */
        padding: 12px 18px;
        margin: 8px 0;
        border-radius: 18px;
        word-wrap: break-word;
        font-size: 0.95em;
        line-height: 1.5;
        box-shadow: 0 1px 1px rgba(0,0,0,0.05);
        color: #ececf1; /* Text color for bubbles */
    }
    .user-bubble {
        background-color: #007bff; /* A distinct blue for user */
        align-self: flex-end;
        margin-left: auto; /* Push to right */
    }
    .bot-bubble {
        background-color: #444654; /* Darker gray for bot */
        align-self: flex-start;
        margin-right: auto; /* Push to left */
    }
    .bot-bubble strong { /* For bolding in welcome messages etc. */
        color: #ececf1;
    }

    /* Welcome screen */
    .welcome-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
        padding: 20px;
        text-align: center;
        color: #8e8ea0;
    }
    .welcome-screen h2 {
        font-size: 2em;
        margin-bottom: 30px;
        color: #ececf1;
    }
    .suggestion-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: center;
        max-width: 700px;
    }
    .suggestion-buttons .stButton button {
        background-color: #444654;
        color: #ececf1;
        border: 1px solid #555;
        padding: 15px 25px;
        border-radius: 10px;
        font-size: 1em;
        font-weight: normal;
        transition: background-color 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .suggestion-buttons .stButton button:hover {
        background-color: #555761;
    }


    /* Input area */
    .input-area-container {
        position: fixed; /* Fixed position relative to viewport */
        bottom: 0;
        left: 260px; /* Adjust based on sidebar width */
        right: 0;
        background: #343541; /* Match main background */
        padding: 15px 20px;
        border-top: 1px solid #444654;
        display: flex;
        align-items: center;
        justify-content: center; /* Center the input group */
        gap: 10px;
        box-sizing: border-box; /* Include padding in width */
    }
    .input-group {
        display: flex;
        align-items: center;
        background-color: #40414f; /* Darker background for input group */
        border-radius: 25px;
        max-width: 700px; /* Limit input width like ChatGPT */
        width: 100%;
        padding: 5px 15px;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
    }
    .input-group .stTextInput > div > div > input {
        border-radius: 25px;
        padding: 12px 15px;
        border: none; /* No border for input */
        background: transparent; /* Transparent background */
        color: #ececf1;
        font-size: 1em;
        flex-grow: 1;
        outline: none; /* Remove outline on focus */
        box-shadow: none; /* Remove box shadow */
    }
    .input-group .stTextInput > div > div > input::placeholder {
        color: #8e8ea0;
    }
    .input-group .stButton > button {
        background: none;
        border: none;
        color: #8e8ea0; /* Gray for icons */
        font-size: 1.5em; /* Larger icons */
        padding: 5px 10px;
        cursor: pointer;
        transition: color 0.2s ease;
    }
    .input-group .stButton > button:hover {
        color: #ececf1;
    }
    /* Specific styling for the send button (last button in group) */
    .input-group .stButton:last-child > button {
        color: #10a37f; /* ChatGPT green for send */
        font-size: 1.8em;
    }
    .input-group .stButton:last-child > button:hover {
        color: #0d8a6e;
    }

    /* Hide Streamlit default elements */
    #MainMenu, header, footer {
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Ensure a chat session exists on load
ensure_chat_exists()

# --- Sidebar (Chat Navigation and Management) ---
with st.sidebar:
    st.markdown("<div class='sidebar-header'>", unsafe_allow_html=True)
    st.markdown("<h2>WiseBuddy</h2>", unsafe_allow_html=True)
    if st.button("💬 New Chat", key="sidebar_new_chat_btn", help="Start a brand new conversation"):
        new_chat()
        st.experimental_rerun()
    st.markdown("</div>")

    # Search functionality
    st.session_state['search_query'] = st.text_input(
        "Search chats",
        value=st.session_state['search_query'],
        placeholder="Search...",
        key="chat_search_input",
        label_visibility="collapsed" # Hide default label
    )
    st.markdown("<div class='sidebar-chat-list'>", unsafe_allow_html=True)

    # Sort chats by timestamp, newest first
    sorted_chats = sorted(
        [item for item in st.session_state['chat_sessions'].items() if not item[1]['archived']],
        key=lambda item: item[1]['timestamp'],
        reverse=True
    )

    for chat_id, chat_data in sorted_chats:
        # Filter by search query
        if st.session_state['search_query'].lower() in chat_data['title'].lower():
            is_active = (chat_id == st.session_state['active_chat'])
            button_class = "active-chat" if is_active else ""

            # Use columns for chat title and action buttons
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                # Chat selection button
                if st.button(chat_data['title'], key=f"select_chat_{chat_id}",
                             help="Click to switch to this chat",
                             use_container_width=True,
                             type="secondary"): # Use secondary type to remove default styling
                    st.session_state['active_chat'] = chat_id
                    st.session_state['show_rename_input'] = {} # Hide rename input on switch
                    st.experimental_rerun()

            with col2:
                # Dropdown menu for Rename, Archive, Delete
                with st.expander("...", expanded=False):
                    if st.button("✏️ Rename", key=f"rename_opt_{chat_id}", use_container_width=True):
                        st.session_state['show_rename_input'][chat_id] = True
                    if st.button("🗄️ Archive", key=f"archive_opt_{chat_id}", use_container_width=True):
                        archive_chat(chat_id)
                    if st.button("🗑️ Delete", key=f"delete_opt_{chat_id}", use_container_width=True):
                        delete_chat(chat_id)

            # Conditional rename input
            if st.session_state['show_rename_input'].get(chat_id):
                with st.container(): # Use a container to group input and button
                    new_title = st.text_input(
                        "New title:",
                        value=chat_data['title'],
                        key=f"rename_input_{chat_id}",
                        label_visibility="collapsed"
                    )
                    if st.button("Save", key=f"save_rename_{chat_id}"):
                        if new_title.strip() and new_title.strip() != chat_data['title']:
                            rename_chat(chat_id, new_title.strip())
                        else:
                            st.session_state['show_rename_input'][chat_id] = False # Hide if no change or empty
                            st.experimental_rerun()


    st.markdown("</div>") # End sidebar-chat-list

    # Sidebar Footer (User Profile/Settings)
    st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("👤 **Mark Comrade**") # Placeholder user name
    if st.button("⬇️ Account Settings"):
        st.info("Account settings functionality would go here!")
    st.markdown("</div>")

# --- Main Chat Area ---
active_chat_data = st.session_state['chat_sessions'][st.session_state['active_chat']]

# Main Header (for current chat title and "Get Plus")
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.markdown(f"<div class='chat-title-display'>{active_chat_data['title']}</div>", unsafe_allow_html=True)
# Example "Get Plus" button
st.button("✨ Get Plus", key="get_plus_btn")
st.markdown("</div>") # End main-header

# Chat messages display area
st.markdown("<div class='chat-messages-container'>", unsafe_allow_html=True)

if not active_chat_data['messages']:
    # Welcome screen when chat is empty
    st.markdown("<div class='welcome-screen'>", unsafe_allow_html=True)
    st.markdown("<h2>What can I help with?</h2>", unsafe_allow_html=True)
    st.markdown("<div class='suggestion-buttons'>", unsafe_allow_html=True)
    if st.button("🖼️ Create image", key="suggest_image"):
        st.session_state.chat_input = "Generate an image of " # Pre-fill input
        st.experimental_rerun()
    if st.button("💡 Make a plan", key="suggest_plan"):
        st.session_state.chat_input = "Help me plan " # Pre-fill input
        st.experimental_rerun()
    if st.button("📄 Summarize text", key="suggest_summarize"):
        st.session_state.chat_input = "Summarize this text: " # Pre-fill input
        st.experimental_rerun()
    if st.button("➕ More ideas", key="suggest_more"):
        st.session_state.chat_input = "Suggest creative ideas for " # Pre-fill input
        st.experimental_rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
else:
    # Display actual messages
    for msg in active_chat_data['messages']:
        if msg['role'] == 'user':
            st.markdown(f"<div class='message-row'><div class='user-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message-row'><div class='bot-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

st.markdown("</div>") # End chat-messages-container

# --- Input Area ---
st.markdown("<div class='input-area-container'>", unsafe_allow_html=True)
st.markdown("<div class='input-group'>", unsafe_allow_html=True)

# Use a form to manage input and button clicks without rerunning on every keystroke
with st.form(key='chat_form', clear_on_submit=True):
    # Hidden label for accessibility, but visually hidden
    user_input = st.text_input(
        "Ask me anything",
        key='user_input_field',
        placeholder='Send a message...',
        label_visibility="collapsed"
    )

    # Separate buttons for multimodal input and send
    col_pre_input, col_post_input = st.columns([0.1, 0.9])
    with col_pre_input:
        st.button("🖼️", key="upload_image_btn", help="Upload an image (Not functional yet)")
    with col_post_input:
        # Streamlit doesn't support placing buttons directly inside st.text_input
        # So we'll put the microphone and send button next to the form
        col_input, col_mic, col_send = st.columns([0.8, 0.1, 0.1])
        with col_mic:
            st.button("🎤", key="voice_input_btn", help="Voice input (Not functional yet)")
        with col_send:
            send_button = st.form_submit_button("⬆️", help="Send message")

# Outside the form, handle logic based on form submission
if send_button and user_input:
    # Add user message
    active_chat_data['messages'].append({'role': 'user', 'content': user_input})

    # Simulate AI response (replace with actual AI call)
    ai_response = f"Hello from WiseBuddy! You said: **{user_input}**."
    active_chat_data['messages'].append({'role': 'assistant', 'content': ai_response})

    # Auto-rename chat if it's "New Chat X" and has its first message
    if active_chat_data['title'].startswith('New Chat') and len(active_chat_data['messages']) == 2:
        truncated_message = user_input.split('\n')[0][:35] # Take first line, truncate
        if len(user_input.split('\n')[0]) > 35:
            truncated_message += "..."
        active_chat_data['title'] = truncated_message

    st.experimental_rerun() # Rerun to display new messages

st.markdown("</div>") # End input-group
st.markdown("</div>") # End input-area-container

