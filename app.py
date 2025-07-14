import streamlit as st
import uuid

st.set_page_config(page_title="WiseBuddy 🤖", layout="wide")

# ------------------ Session State ------------------ #
if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = {}
    st.session_state['active_chat'] = None
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ''

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
    return f"🧠 WiseBuddy says: {user_message[::-1]}"  # fun demo reply

# Ensure one chat exists
if not st.session_state['chat_sessions']:
    new_chat()

# ------------------ Sidebar ------------------ #
st.sidebar.title("💬 Conversations")
for chat_id, chat in st.session_state['chat_sessions'].items():
    if st.sidebar.button(chat['title'], key=chat_id):
        st.session_state['active_chat'] = chat_id

if st.sidebar.button("➕ New Chat"):
    new_chat()

active_chat_id = st.session_state['active_chat']
active_chat = st.session_state['chat_sessions'][active_chat_id]

st.markdown("""<h1 style='margin-top:-10px;'>🤖 WiseBuddy</h1>""", unsafe_allow_html=True)

# ------------------ Display Messages ------------------ #
for msg in active_chat['messages']:
    bubble_style = """display: inline-block; padding: 10px 15px; border-radius: 15px;
                      margin: 8px 0; max-width: 75%; font-size: 16px; line-height: 1.5;"""
    if msg['role'] == 'user':
        st.markdown(
            f"<div style='{bubble_style} background:#dcf8c6; color:#000; float:right; clear:both;'>{msg['content']}</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='{bubble_style} background:#f1f0f0; color:#000; float:left; clear:both;'>{msg['content']}</div>",
            unsafe_allow_html=True)

# ------------------ Handle Send ------------------ #
def handle_send():
    user_input = st.session_state.input_text.strip()
    if user_input:
        active_chat['messages'].append({'role': 'user', 'content': user_input})
        bot_reply = generate_reply(user_input)
        active_chat['messages'].append({'role': 'assistant', 'content': bot_reply})
        
        # Auto rename
        user_msgs = [m for m in active_chat['messages'] if m['role'] == 'user']
        if len(user_msgs) == 3:
            rename_chat(active_chat_id, user_msgs[0]['content'][:30] + "...")
    
    st.session_state.input_text = ''
    st.experimental_rerun()

# ------------------ Input & Button ------------------ #
col1, col2 = st.columns([10, 1])
with col1:
    st.text_input("Ask me anything...", key="input_text", label_visibility="collapsed", on_change=handle_send)
with col2:
    st.button("🛩️", on_click=handle_send, use_container_width=True)

# ------------------ Scroll ------------------ #
st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
