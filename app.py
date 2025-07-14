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

# Main area layout and styling
st.markdown("""
    <style>
    .chat-bubble {
        max-width: 70%;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 15px;
        font-size: 16px;
        line-height: 1.4;
    }
    .user {
        background-color: #dcf8c6;
        color: black;
        align-self: flex-end;
        margin-left: auto;
    }
    .bot {
        background-color: #f1f0f0;
        color: black;
        align-self: flex-start;
        margin-right: auto;
    }
    .input-container {
        position: fixed;
        bottom: 20px;
        left: 250px;
        right: 20px;
        display: flex;
        align-items: center;
        background: white;
        border: 1px solid #ddd;
        border-radius: 25px;
        padding: 5px 10px;
        z-index: 999;
    }
    .input-container input {
        border: none;
        outline: none;
        flex: 1;
        padding: 10px;
        font-size: 16px;
        border-radius: 25px;
    }
    .input-container button {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #007bff;
        margin-left: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Display chat bubbles
st.markdown("<div style='display:flex; flex-direction:column;'>", unsafe_allow_html=True)
active_chat_id = st.session_state['active_chat']
active_chat = st.session_state['chat_sessions'][active_chat_id]

for msg in active_chat['messages']:
    role_class = "user" if msg['role'] == 'user' else "bot"
    st.markdown(f"<div class='chat-bubble {role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Custom input + paper plane send button
st.markdown("""
    <div class='input-container'>
        <form action="" method="post">
            <input name="user_input" id="user_input" placeholder="Ask me anything..." autocomplete="off" />
            <button type="submit">🛩️</button>
        </form>
    </div>
    <script>
        const input = window.parent.document.querySelector('input[name=user_input]');
        const form = window.parent.document.querySelector('form');
        form.onsubmit = function(e) {
            e.preventDefault();
            const value = input.value;
            if (value) {
                window.parent.postMessage({type: 'user_input', value: value}, '*');
                input.value = '';
            }
        };
    </script>
""", unsafe_allow_html=True)

# Fallback for actual input value (Streamlit backend handling)
user_input = st.text_input("", label_visibility='collapsed', key="chat_input_placeholder")
send = st.button("➤ Send", key="send_button_placeholder")
if send and user_input:
    active_chat['messages'].append({'role': 'user', 'content': user_input})
    bot_reply = generate_reply(user_input)
    active_chat['messages'].append({'role': 'assistant', 'content': bot_reply})
    user_messages = [m for m in active_chat['messages'] if m['role'] == 'user']
    if len(user_messages) == 3:
        rename_chat(active_chat_id, user_messages[0]['content'][:20] + '...')
    st.experimental_rerun()

st.markdown("<script>window.scrollTo(0,document.body.scrollHeight);</script>", unsafe_allow_html=True)
