import streamlit as st
import uuid

# ------------------------ Page Setup ------------------------ #
st.set_page_config(page_title="WiseBuddy", layout="wide")

# ------------------------ Session State Setup ------------------------ #
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    st.session_state['active_chat'] = None

# ------------------------ Chat Logic ------------------------ #
def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state['chat_sessions'][chat_id] = {
        'title': 'New Chat',
        'messages': []
    }
    st.session_state['active_chat'] = chat_id

def rename_chat(chat_id, new_title):
    st.session_state['chat_sessions'][chat_id]['title'] = new_title

def generate_reply(user_message):
    return f"Echo: {user_message}"

# Ensure one chat exists
if not st.session_state['chat_sessions']:
    new_chat()

# ------------------------ Sidebar ------------------------ #
st.sidebar.title("💬 WiseBuddy Chats")
for chat_id, chat in st.session_state['chat_sessions'].items():
    if st.sidebar.button(chat['title'], key=chat_id):
        st.session_state['active_chat'] = chat_id

if st.sidebar.button("➕ New Chat"):
    new_chat()

# ------------------------ Active Chat ------------------------ #
active_chat_id = st.session_state['active_chat']
active_chat = st.session_state['chat_sessions'][active_chat_id]

st.markdown("<h2 style='margin-top:-10px;'>🤖 WiseBuddy</h2>", unsafe_allow_html=True)

# ------------------------ Chat Bubbles ------------------------ #
for msg in active_chat['messages']:
    if msg['role'] == 'user':
        st.markdown(
            f"<div style='background:#dcf8c6;padding:10px 15px;margin:8px 0;border-radius:12px;max-width:70%;margin-left:auto;color:#000;'>{msg['content']}</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='background:#f1f0f0;padding:10px 15px;margin:8px 0;border-radius:12px;max-width:70%;margin-right:auto;color:#000;'>{msg['content']}</div>",
            unsafe_allow_html=True)

# ------------------------ Input Field with Send ------------------------ #
col1, col2 = st.columns([10, 1])
with col1:
    user_input = st.text_input("Ask me anything...", key="chat_input", label_visibility="collapsed")
with col2:
    send = st.button("🛩️", use_container_width=True)

if send and user_input:
    # Save user message
    active_chat['messages'].append({'role': 'user', 'content': user_input})
    
    # Bot reply
    bot_reply = generate_reply(user_input)
    active_chat['messages'].append({'role': 'assistant', 'content': bot_reply})
    
    # Auto-rename after 3 user messages
    user_msgs = [m for m in active_chat['messages'] if m['role'] == 'user']
    if len(user_msgs) == 3:
        rename_chat(active_chat_id, user_msgs[0]['content'][:20] + "...")

    # Clear input and rerun
    st.session_state['chat_input'] = ''
    st.experimental_rerun()

# ------------------------ Auto Scroll ------------------------ #
st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
