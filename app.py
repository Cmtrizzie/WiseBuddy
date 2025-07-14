import streamlit as st
import uuid
import google.generativeai as genai

# ---- CONFIG ---- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide")

# ---- GEMINI API SETUP ---- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# ---- SESSION STATE ---- #
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

def generate_reply_with_gemini(user_message):
    try:
        prompt = f"{user_message}\n\nRespond in a helpful and friendly way. Use emojis where appropriate!"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini error: {str(e)}"

# ---- Ensure At Least One Chat Exists ---- #
if not st.session_state['chat_sessions']:
    new_chat()

# ---- SIDEBAR ---- #
st.sidebar.title("💬 Conversations")
for chat_id, chat in st.session_state['chat_sessions'].items():
    if st.sidebar.button(chat['title'], key=chat_id):
        st.session_state['active_chat'] = chat_id

if st.sidebar.button("➕ New Chat"):
    new_chat()

# ---- ACTIVE CHAT ---- #
active_chat_id = st.session_state['active_chat']
active_chat = st.session_state['chat_sessions'][active_chat_id]

st.markdown("<h1 style='margin-top:-10px;'>🤖 WiseBuddy</h1>", unsafe_allow_html=True)

# ---- DISPLAY CHAT MESSAGES ---- #
bubble_style = """display: inline-block; padding: 10px 15px; border-radius: 15px;
                  margin: 8px 0; max-width: 75%; font-size: 16px; line-height: 1.5;"""

message_placeholder = st.empty()
with message_placeholder.container():
    for msg in active_chat['messages']:
        if msg['role'] == 'user':
            st.markdown(
                f"<div style='{bubble_style} background:#dcf8c6; color:#000; float:right; clear:both;'>{msg['content']}</div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='{bubble_style} background:#f1f0f0; color:#000; float:left; clear:both;'>{msg['content']}</div>",
                unsafe_allow_html=True)

# ---- SEND HANDLER ---- #
def handle_send():
    user_input = st.session_state.input_text.strip()
    if user_input:
        active_chat['messages'].append({'role': 'user', 'content': user_input})
        reply = generate_reply_with_gemini(user_input)
        active_chat['messages'].append({'role': 'assistant', 'content': reply})

        user_msgs = [m for m in active_chat['messages'] if m['role'] == 'user']
        if len(user_msgs) == 3:
            rename_chat(active_chat_id, user_msgs[0]['content'][:30] + "...")

    st.session_state.input_text = ''

# ---- STYLE FOR WHATSAPP-LIKE INPUT ---- #
st.markdown("""
<style>
.input-container {
    display: flex;
    align-items: center;
    gap: 5px;
    width: 100%;
}
input.chat-input {
    flex-grow: 1;
    padding: 10px 15px;
    font-size: 16px;
    border-radius: 25px;
    border: 1px solid #ccc;
    outline: none;
}
button.send-btn {
    background-color: #25D366;
    color: white;
    border: none;
    padding: 0 15px;
    height: 42px;
    font-size: 20px;
    border-radius: 50%;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ---- MESSAGE INPUT BAR ---- #
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([10, 1])
    with col1:
        user_input = st.text_input("Type a message...", key="input_text", label_visibility="collapsed")
    with col2:
        submitted = st.form_submit_button("🛩️", use_container_width=True)

if submitted:
    handle_send()

# ---- AUTO SCROLL TARGET ---- #
st.markdown("<div id='end-of-chat'></div>", unsafe_allow_html=True)
