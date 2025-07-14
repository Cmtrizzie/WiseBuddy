import streamlit as st
import uuid
import google.generativeai as genai

# --- CONFIG --- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide")

# --- GEMINI API --- #
# Assuming GEMINI_API_KEY is correctly set in st.secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# --- SESSION --- #
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.active_chat = None

def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_chat = chat_id

def rename_chat(chat_id, title):
    st.session_state.chat_sessions[chat_id]["title"] = title

def generate_reply(user_input):
    try:
        chat = model.start_chat()
        response = chat.send_message(user_input)
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):
            return "🚫 API quota limit reached. Please wait a bit and try again!"
        return f"⚠️ Gemini error: {str(e)}"

# --- INIT DEFAULT CHAT --- #
if not st.session_state.chat_sessions:
    new_chat()

active_id = st.session_state.active_chat
active_chat = st.session_state.chat_sessions[active_id]

# --- STYLING --- #
st.markdown("""
<style>
body, .main, .block-container, [data-testid="stAppViewContainer"] {
    background-color: #000000 !important; /* Deeper black for consistency */
    color: white !important;
}

/* Hide Streamlit's default header and footer */
[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}
[data-testid="stDecoration"] {
    display: none !important;
}

.custom-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background-color: #000000;
    position: sticky;
    top: 0;
    z-index: 1000;
    color: white;
}
.header-icon {
    font-size: 24px;
    cursor: pointer;
    padding: 5px;
}
.header-title {
    font-size: 18px;
    font-weight: 500;
}

.chat-container {
    padding-bottom: 120px; /* Space for the fixed input bar */
    padding-top: 20px; /* Give some space below the header */
    max-width: 800px; /* Limit chat width for better readability */
    margin: 0 auto; /* Center the chat container */
}
.message {
    max-width: 70%; /* Slightly narrower message bubbles */
    padding: 12px 16px;
    border-radius: 20px;
    margin: 10px 0;
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
}
.user {
    background-color: #1e1e1e; /* Darker grey for user messages */
    margin-left: auto;
    text-align: right;
    border-bottom-right-radius: 5px; /* Slightly less round on one corner */
}
.bot {
    background-color: #2b2b2b; /* Slightly lighter grey for bot messages */
    margin-right: auto;
    text-align: left;
    border-bottom-left-radius: 5px; /* Slightly less round on one corner */
}

.welcome-message {
    text-align: center;
    margin-top: 25vh;
    color: gray;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.welcome-message h3 {
    color: white;
    margin-top: 15px;
    margin-bottom: 5px;
    font-size: 24px;
}
.welcome-message p {
    font-size: 16px;
    color: #888;
}

.input-box {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #0d0d0d;
    padding: 16px 20px; /* More padding for a consistent look */
    border-top: 1px solid #222;
    z-index: 1000;
    display: flex;
    justify-content: center; /* Center the input field */
}
.input-field-container {
    display: flex;
    align-items: center;
    background: #1f1f1f;
    border-radius: 30px;
    padding: 8px 12px; /* Adjusted padding */
    width: 100%;
    max-width: 760px; /* Match chat container width visually */
}
input[type="text"] {
    flex-grow: 1;
    background: transparent;
    border: none;
    outline: none;
    color: white;
    font-size: 16px;
    padding: 0 10px; /* Padding inside the text input */
}
input[type="text"]::placeholder {
    color: #888;
}

.send-button {
    background-color: #2563eb; /* A blue that stands out on dark */
    color: white;
    border: none;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    font-size: 18px;
    margin-left: 10px;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0; /* Prevent shrinking on smaller screens */
}

/* Custom buttons for "DeepThink" and "Search" styling */
.custom-button-container {
    display: flex;
    gap: 10px; /* Space between buttons */
    margin-top: 10px; /* Space above input field */
    justify-content: center;
    width: 100%;
    max-width: 760px; /* Match input width */
}
.stButton>button {
    background-color: #2b2b2b; /* Darker button background */
    color: white;
    border: 1px solid #444; /* Subtle border */
    border-radius: 20px;
    padding: 8px 15px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s ease;
}
.stButton>button:hover {
    background-color: #3a3a3a;
}
.stButton>button:focus:not(:active) {
    border-color: #2563eb;
    box-shadow: none;
}


::-webkit-scrollbar {
    width: 5px;
}
::-webkit-scrollbar-thumb {
    background: #333;
    border-radius: 10px;
}
::-webkit-scrollbar-track {
    background: #111;
}

/* Adjust Streamlit's internal form rendering for better layout */
div.stForm {
    width: 100%;
    margin-top: 0;
    margin-bottom: 0;
}
div.stForm > div {
    display: flex;
    flex-direction: column; /* Stack elements within the form */
    align-items: center;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# --- CUSTOM HEADER --- #
st.markdown("""
<div class="custom-header">
    <div class="header-icon">☰</div>
    <div class="header-title">New chat</div>
    <div class="header-icon">+</div>
</div>
""", unsafe_allow_html=True)


# --- WELCOME MESSAGE / CHAT MESSAGES --- #
if len(active_chat["messages"]) == 0:
    # Changed to use a custom div for better centering and styling
    st.markdown("""
        <div class='welcome-message'>
            <img src='https://emojicdn.elk.sh/🤖' width='72'>
            <h3>Hello, I'm WiseBuddy</h3>
            <p>How can I assist you today?</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in active_chat["messages"]:
        role = "user" if msg["role"] == "user" else "bot"
        st.markdown(f"<div class='message {role}'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- INPUT BAR --- #
st.markdown('<div class="input-box">', unsafe_allow_html=True)
# Add placeholder buttons similar to DeepSeek's "DeepThink (R1)" and "Search"
st.markdown("""
    <div class="custom-button-container">
        <button class="stButton" style="min-width: unset;"><span>DeepThink (R1)</span></button>
        <button class="stButton" style="min-width: unset;"><span>🌍 Search</span></button>
    </div>
""", unsafe_allow_html=True) # Using button tag directly for better styling control

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([10, 1])
    with col1:
        # Wrap input in a div for consistent styling with the send button
        st.markdown('<div class="input-field-container">', unsafe_allow_html=True)
        user_input = st.text_input("Message", "", label_visibility="collapsed", key="input_text", placeholder="Message WiseBuddy")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        # Custom button to match the circular send button
        send = st.form_submit_button("➤", help="Send message")
        st.markdown("""
            <style>
                .stButton > button[kind="primary"] { /* Target the specific send button */
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 42px;
                    height: 42px;
                    font-size: 18px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-left: 0; /* Adjust margin as needed */
                    padding: 0;
                }
                .stButton > button[kind="primary"]:hover {
                    background-color: #1a56c7; /* Darker blue on hover */
                }
            </style>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# --- HANDLE SEND --- #
if send and user_input.strip():
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    # Streamlit re-runs the script on state changes, so we need to add messages
    # and then immediately rerun to display them.
    # The actual generation is done only once when the form is submitted.
    response = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": response})

    # Rename chat after the third user message
    user_message_count = len([m for m in active_chat["messages"] if m["role"] == "user"])
    if user_message_count == 3:
        rename_chat(active_id, active_chat["messages"][0]["content"][:30] + "...")

    st.rerun() # Rerun to display new messages

