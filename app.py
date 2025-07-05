import streamlit as st
import random
import uuid

# --- Initialize Session State for Multiple Chats ---
# 'chat_sessions' stores all chat data, keyed by a unique ID
# 'active_chat' stores the ID of the currently selected chat
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    st.session_state['active_chat'] = None

# --- Helper Functions for Chat Management ---

def new_chat():
    """Creates a new chat session and sets it as active."""
    chat_id = str(uuid.uuid4())
    st.session_state['chat_sessions'][chat_id] = {
        'title': f'New Chat {len(st.session_state["chat_sessions"]) + 1}', # Dynamic title
        'messages': []
    }
    st.session_state['active_chat'] = chat_id
    # st.experimental_rerun() # Rerun immediately to show new chat selected

def ensure_chat_exists():
    """Ensures there's always at least one chat session and an active chat."""
    if not st.session_state['chat_sessions']:
        new_chat()
    if st.session_state['active_chat'] not in st.session_state['chat_sessions']:
        st.session_state['active_chat'] = next(iter(st.session_state['chat_sessions']))

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for ChatGPT-like Styling ---
st.markdown("""
<style>
    /* General layout adjustments */
    .stApp {
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: row; /* Sidebar and main content side-by-side */
    }
    .stSidebar {
        width: 280px !important; /* Fixed width for sidebar */
        min-width: 280px !important;
        max-width: 280px !important;
        background-color: #202123; /* Dark background for sidebar */
        color: #ececf1;
        padding-top: 20px;
        box-shadow: 2px 0 5px rgba(0,0,0,0.2);
    }
    .css-1d391kg { /* Target for main content area to take remaining width */
        flex-grow: 1;
        padding: 0; /* Remove default padding */
        display: flex;
        flex-direction: column;
        height: 100vh; /* Full viewport height */
    }

    /* Sidebar specific styling */
    .stSidebar button {
        width: 100%;
        text-align: left;
        background-color: #343541; /* Darker button for chat items */
        color: #ececf1;
        border: none;
        padding: 10px 15px;
        margin-bottom: 5px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    .stSidebar button:hover {
        background-color: #444654;
    }
    .stSidebar button.active-chat { /* Style for the active chat button */
        background-color: #444654;
        font-weight: bold;
    }
    .sidebar-new-chat-btn { /* Style for the "+ New Chat" button */
        background-color: #00A67E !important; /* Brighter green for new chat */
        color: white !important;
        margin-top: 15px;
        padding: 12px 15px !important;
    }
    .sidebar-new-chat-btn:hover {
        background-color: #008f6c !important;
    }

    /* Main chat area */
    .chat-header {
        background-color: #f1f0f0;
        padding: 15px 20px;
        border-bottom: 1px solid #ddd;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        color: #333;
    }
    .chat-messages-container {
        flex-grow: 1; /* Takes up available space */
        overflow-y: auto; /* Scroll for messages */
        padding: 20px;
        background-color: #fff;
    }
    .user-bubble, .bot-bubble {
        max-width: 75%; /* Slightly wider bubbles */
        padding: 12px 18px;
        margin: 8px 0;
        border-radius: 18px; /* More rounded corners */
        word-wrap: break-word;
        font-size: 0.95em;
        line-height: 1.5;
        box-shadow: 0 1px 1px rgba(0,0,0,0.05); /* Subtle shadow */
    }
    .user-bubble {
        background-color: #dcf8c6; /* Light green */
        align-self: flex-end;
        margin-left: auto; /* Push to right */
        color: #333;
    }
    .bot-bubble {
        background-color: #f1f0f0; /* Light gray */
        align-self: flex-start;
        margin-right: auto; /* Push to left */
        color: #333;
    }
    .message-row {
        display: flex;
        width: 100%;
    }

    /* Input area */
    .input-area-container {
        position: sticky; /* Make it stick to the bottom */
        bottom: 0;
        width: 100%;
        background: #fff;
        padding: 15px 20px;
        border-top: 1px solid #ddd;
        display: flex;
        align-items: center;
        gap: 10px; /* Space between input and button */
        box-sizing: border-box; /* Include padding in width */
    }
    .input-area-container .stTextInput > div > div > input {
        border-radius: 25px; /* Fully rounded input */
        padding: 12px 20px;
        border: 1px solid #ccc;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
        font-size: 1em;
        flex-grow: 1; /* Take up available space */
    }
    .input-area-container .stButton > button {
        background-color: #10a37f; /* ChatGPT green */
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.2s ease;
    }
    .input-area-container .stButton > button:hover {
        background-color: #0d8a6e;
    }
    .stHeader { /* Hide default Streamlit header */
        display: none;
    }
    /* Hide the Streamlit footer watermark */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Ensure a chat session exists on load
ensure_chat_exists()

# --- Sidebar (Chat Navigation) ---
with st.sidebar:
    st.markdown("## Your Chats")

    # "+ New Chat" button at the top of the sidebar
    if st.button("+ New Chat", key="new_chat_sidebar", help="Start a brand new conversation"):
        new_chat()
        st.experimental_rerun()

    st.markdown("---") # Separator

    # List existing chats
    for chat_id, chat in st.session_state['chat_sessions'].items():
        is_active = (chat_id == st.session_state['active_chat'])
        button_class = "active-chat" if is_active else ""

        col1, col2 = st.columns([0.8, 0.2]) # For title and delete button
        with col1:
            if st.button(chat['title'], key=f"select_chat_{chat_id}", help="Click to switch to this chat",
                         use_container_width=True):
                st.session_state['active_chat'] = chat_id
                st.experimental_rerun()
        with col2:
            if st.button("🗑️", key=f"delete_chat_{chat_id}", help="Delete this chat", use_container_width=True):
                if st.session_state['active_chat'] == chat_id:
                    # If deleting active chat, switch to another or create new
                    chat_ids = list(st.session_state['chat_sessions'].keys())
                    idx = chat_ids.index(chat_id)
                    st.session_state['chat_sessions'].pop(chat_id)
                    if chat_ids: # If there are other chats
                        if idx > 0:
                            st.session_state['active_chat'] = chat_ids[idx - 1]
                        elif len(chat_ids) > 1: # If first item was deleted and others exist
                            st.session_state['active_chat'] = chat_ids[1]
                        else: # No other chats, create new one
                            new_chat()
                    else: # No chats left, create a new one
                        new_chat()
                else: # Deleting a non-active chat
                    st.session_state['chat_sessions'].pop(chat_id)
                st.experimental_rerun()

# --- Main Chat Area ---
active_chat_data = st.session_state['chat_sessions'][st.session_state['active_chat']]

# Chat Header (with potential rename functionality)
st.markdown(f"<div class='chat-header'>{active_chat_data['title']}</div>", unsafe_allow_html=True)

# Chat messages display area
with st.container(): # Use a container for the scrollable chat area
    st.markdown("<div class='chat-messages-container'>", unsafe_allow_html=True)
    for msg in active_chat_data['messages']:
        if msg['role'] == 'user':
            st.markdown(f"<div class='message-row'><div class='user-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message-row'><div class='bot-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Input Area ---
# This part is placed outside the main container to ensure it's always at the bottom
with st.container():
    st.markdown("<div class='input-area-container'>", unsafe_allow_html=True)
    user_input = st.text_input("Message ChatGPT...", key='chat_input',
                                placeholder='Type your message here...',
                                label_visibility="collapsed") # Hide default label

    # Use a form to capture text input and button click
    # This prevents rerunning on every keystroke
    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2 = st.columns([1, 0.1])
        with col1:
            user_input = st.text_input("Your message", label_visibility="collapsed",
                                        placeholder="Send a message...", key="user_input_field")
        with col2:
            send_button = st.form_submit_button("⬆️", help="Send message")

    if send_button and user_input:
        # Add user message
        active_chat_data['messages'].append({'role': 'user', 'content': user_input})

        # Simulate AI response (replace with actual AI call)
        ai_response = f"I received: {user_input}"
        active_chat_data['messages'].append({'role': 'assistant', 'content': ai_response})

        # Auto-rename chat if it's "New Chat X" and has its first message
        if active_chat_data['title'].startswith('New Chat') and len(active_chat_data['messages']) == 2: # User + AI message
            # A simple way to generate a new title based on the first user message
            truncated_message = user_input[:30] + '...' if len(user_input) > 30 else user_input
            active_chat_data['title'] = truncated_message

        st.experimental_rerun() # Rerun to display new messages

    st.markdown("</div>", unsafe_allow_html=True)

