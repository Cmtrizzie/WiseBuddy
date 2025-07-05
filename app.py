import streamlit as st
import random
import uuid

# Initialize session state for multiple chats
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    st.session_state['active_chat'] = None

# Function to create a new chat
def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state['chat_sessions'][chat_id] = {
        'title': 'New Chat',
        'messages': []
    }
    st.session_state['active_chat'] = chat_id

# Function to delete a chat
def delete_chat(chat_id):
    if chat_id in st.session_state['chat_sessions']:
        del st.session_state['chat_sessions'][chat_id]
        if st.session_state['active_chat'] == chat_id:
            st.session_state['active_chat'] = next(iter(st.session_state['chat_sessions']), None)

# Function to rename a chat
def rename_chat(chat_id, new_title):
    if chat_id in st.session_state['chat_sessions']:
        st.session_state['chat_sessions'][chat_id]['title'] = new_title

# Sidebar for chat selection
st.sidebar.title("💬 Chats")
for chat_id, chat in st.session_state['chat_sessions'].items():
    if st.sidebar.button(chat['title'], key=chat_id):
        st.session_state['active_chat'] = chat_id

if st.sidebar.button("➕ New Chat"):
    new_chat()

# Main area
st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 80vh;
        border: 1px solid #ddd;
        padding: 10px;
        overflow-y: auto;
        background-color: #f9f9f9;
        border-radius: 10px;
    }
    .input-container {
        display: flex;
        margin-top: 10px;
    }
    .input-box {
        flex: 1;
        padding: 10px;
        border-radius: 20px;
        border: 1px solid #ccc;
        margin-right: 10px;
    }
    .send-button {
        padding: 10px 20px;
        border-radius: 20px;
        border: none;
        background-color: #4CAF50;
        color: white;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state['active_chat']:
    active_chat = st.session_state['chat_sessions'][st.session_state['active_chat']]

    st.title(active_chat['title'])

    # Chat display
    chat_placeholder = st.empty()
    with chat_placeholder.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for msg in active_chat['messages']:
            role = "You" if msg['role'] == 'user' else "WiseBuddy"
            st.markdown(f"**{role}:** {msg['content']}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Input box with auto-scroll trigger
    user_input = st.text_input("", key='chat_input', placeholder="Type your message and press Send")
    send_col, empty_col = st.columns([1, 10])
    if send_col.button("Send"):
        if user_input:
            active_chat['messages'].append({'role': 'user', 'content': user_input})
            bot_reply = f"Echo: {user_input}"
            active_chat['messages'].append({'role': 'assistant', 'content': bot_reply})
            if len([m for m in active_chat['messages'] if m['role'] == 'user']) == 3:
                rename_chat(st.session_state['active_chat'], user_input[:20] + '...')
            st.session_state['chat_input'] = ''
            st.experimental_rerun()
else:
    st.title("Welcome to WiseBuddy 🤖")
    st.write("Your personal thinking partner. Start a new chat to begin.")
