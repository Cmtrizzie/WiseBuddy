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
    st.session_state['chat_sessions'].pop(chat_id, None)
    if st.session_state['active_chat'] == chat_id:
        st.session_state['active_chat'] = next(iter(st.session_state['chat_sessions']), None)

# Function to rename a chat
def rename_chat(chat_id, new_title):
    st.session_state['chat_sessions'][chat_id]['title'] = new_title

# Ensure there's always an active chat
def ensure_chat():
    if not st.session_state['chat_sessions']:
        new_chat()
    if not st.session_state['active_chat']:
        st.session_state['active_chat'] = next(iter(st.session_state['chat_sessions']))

ensure_chat()

# Sidebar for chat selection
st.sidebar.title("Chats")
for chat_id, chat in st.session_state['chat_sessions'].items():
    selected = chat_id == st.session_state['active_chat']
    if st.sidebar.button(chat['title'], key=chat_id):
        st.session_state['active_chat'] = chat_id
st.sidebar.divider()
if st.sidebar.button("+ New Chat"):
    new_chat()
    st.experimental_rerun()

# Main layout CSS to mimic ChatGPT
st.markdown("""
<style>
body { margin: 0; }
.main { padding: 0; }
.chat-container { display: flex; flex-direction: column; height: 80vh; overflow-y: auto; padding: 10px; }
.user-bubble, .bot-bubble { max-width: 70%; padding: 10px 15px; margin: 5px 0; border-radius: 12px; word-wrap: break-word; }
.user-bubble { background-color: #dcf8c6; align-self: flex-end; }
.bot-bubble { background-color: #f1f0f0; align-self: flex-start; }
.input-area { position: fixed; bottom: 0; left: 200px; right: 0; background: #fff; padding: 10px; display: flex; align-items: center; border-top: 1px solid #ddd; }
.input-field { flex: 1; padding: 10px 15px; border-radius: 20px; border: 1px solid #ccc; margin-right: 10px; }
.send-btn { background-color: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 20px; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# Active chat content
active = st.session_state['chat_sessions'][st.session_state['active_chat']]
st.header(active['title'])

# Chat messages area
chat_placeholder = st.empty()
with chat_placeholder.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in active['messages']:
        if msg['role'] == 'user':
            st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Input area styled with markdown
st.markdown("<div class='input-area'>", unsafe_allow_html=True)
user_input = st.text_input("Ask me anything", key='input', placeholder='Ask me anything')
send_clicked = st.button("Send")
st.markdown("</div>", unsafe_allow_html=True)

# Handle message sending
if send_clicked or (user_input and not st.session_state.get('input_sent')):
    if user_input.strip():
        active['messages'].append({'role': 'user', 'content': user_input})
        active['messages'].append({'role': 'assistant', 'content': f"Echo: {user_input}"})
        st.session_state['input'] = ''
        st.session_state['input_sent'] = True
        st.experimental_rerun()
else:
    st.session_state['input_sent'] = False
