import streamlit as st
import random
import uuid

st.set_page_config(page_title="WiseBuddy", layout="wide")

# Initialize session state
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

# Function to rename chat
def rename_chat(chat_id, new_title):
    st.session_state['chat_sessions'][chat_id]['title'] = new_title

# Function to generate bot reply
def generate_reply(user_message):
    return f"Echo: {user_message}"

# Ensure at least one chat exists
if not st.session_state['chat_sessions']:
    new_chat()

# Sidebar - chat list and new chat button
st.sidebar.title("💬 WiseBuddy Chats")
for chat_id, chat in st.session_state['chat_sessions'].items():
    label = chat['title']
    if st.sidebar.button(label, key=chat_id):
        st.session_state['active_chat'] = chat_id

if st.sidebar.button("➕ New Chat"):
    new_chat()

# Main area
active_chat_id = st.session_state['active_chat']
active_chat = st.session_state['chat_sessions'][active_chat_id]

st.title("🤖 WiseBuddy")

# Display chat bubbles
for msg in active_chat['messages']:
    if msg['role'] == 'user':
        st.markdown(f"<div style='text-align: right; background: #dcf8c6; padding:10px; border-radius:10px; margin:5px;'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left; background: #f1f0f0; padding:10px; border-radius:10px; margin:5px;'>{msg['content']}</div>", unsafe_allow_html=True)

# Input field with Send button
col1, col2 = st.columns([10,1])
with col1:
    user_input = st.text_input("", placeholder="Ask me anything...", key="chat_input", label_visibility="collapsed")
with col2:
    send_clicked = st.button("➤", key="send_btn")

if send_clicked and user_input:
    active_chat['messages'].append({'role': 'user', 'content': user_input})
    bot_reply = generate_reply(user_input)
    active_chat['messages'].append({'role': 'assistant', 'content': bot_reply})

    # Auto rename after 3 user messages
    user_messages = [m for m in active_chat['messages'] if m['role'] == 'user']
    if len(user_messages) == 3:
        rename_chat(active_chat_id, user_messages[0]['content'][:20] + '...')

    st.session_state['chat_input'] = ''
    st.experimental_rerun()

st.markdown("<script>window.scrollTo(0,document.body.scrollHeight);</script>", unsafe_allow_html=True)
