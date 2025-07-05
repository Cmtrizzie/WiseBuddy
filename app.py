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

# Active chat area
if st.session_state['active_chat']:
    active_chat = st.session_state['chat_sessions'][st.session_state['active_chat']]
    st.title(active_chat['title'])

    # Display messages
    for msg in active_chat['messages']:
        role = "You" if msg['role'] == 'user' else "WiseBuddy"
        st.markdown(f"**{role}:** {msg['content']}")

    # Input and send button inside text_input container
    col1, col2 = st.columns([9, 1])
    with col1:
        user_input = st.text_input("", key='chat_input', placeholder="Type your message and press Enter...")
    with col2:
        if st.button("➡️", key='send_button'):
            if user_input:
                active_chat['messages'].append({'role': 'user', 'content': user_input})
                bot_reply = f"Echo: {user_input}"
                active_chat['messages'].append({'role': 'assistant', 'content': bot_reply})
                if len([m for m in active_chat['messages'] if m['role'] == 'user']) == 3:
                    rename_chat(st.session_state['active_chat'], user_input[:20] + '...')
                st.session_state['chat_input'] = ''
                st.experimental_rerun()

    # Rename & delete controls
    if st.sidebar.button("✏️ Rename Chat", key=f'rename_{st.session_state["active_chat"]}'):
        new_title = st.text_input("Enter new chat name:", key='rename_input')
        if new_title:
            rename_chat(st.session_state['active_chat'], new_title)
            st.experimental_rerun()

    if st.sidebar.button("🗑️ Delete Chat", key=f'delete_{st.session_state["active_chat"]}'):
        delete_chat(st.session_state['active_chat'])
        st.experimental_rerun()

else:
    st.title("Welcome to WiseBuddy 🤖")
    st.write("Your personal thinking partner. Start a new chat to begin.")

    # Input and send button always visible
    col1, col2 = st.columns([9, 1])
    with col1:
        placeholder_input = st.text_input("", key='welcome_input', placeholder="Type here and press Enter...")
    with col2:
        st.button("➡️", key='welcome_send')
