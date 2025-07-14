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

/* Custom Header (as per previous iteration, kept for consistency) */
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

/* --- Input Box Styling --- */
.input-box {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #0d0d0d; /* Dark background for the fixed bar */
    padding: 16px 20px; /* Padding around the input field */
    border-top: 1px solid #222; /* Subtle top border */
    z-index: 1000;
    display: flex;
    justify-content: center; /* Center the content of the input bar */
    align-items: center; /* Vertically center content */
}

.input-field-wrapper { /* New wrapper for the input and button to control width */
    display: flex;
    align-items: center;
    width: 100%;
    max-width: 760px; /* Max width for the input field to match chat container */
    background: #1f1f1f; /* Background for the input area itself */
    border-radius: 30px; /* Rounded corners for the input field */
    padding: 8px 12px; /* Padding inside the input wrapper */
}

input[type="text"] {
    flex-grow: 1; /* Allows the text input to take available space */
    background: transparent; /* No background for the input element itself */
    border: none; /* No border */
    outline: none; /* No outline on focus */
    color: white; /* Text color */
    font-size: 16px;
    padding: 0 10px; /* Padding inside the text input for spacing */
}
input[type="text"]::placeholder {
    color: #888; /* Placeholder text color */
}

.send-button {
    background-color: #2563eb; /* Blue send button */
    color: white;
    border: none;
    border-radius: 50%; /* Circular button */
    width: 42px;
    height: 42px;
    font-size: 18px;
    margin-left: 10px; /* Space between input and button */
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0; /* Prevent shrinking */
}

/* Remove styling for the previously added custom buttons, as they are gone */
.custom-button-container {
    display: none; /* Hide this container */
}
.stButton>button {
    display: none; /* Hide specific streamlit buttons that might inherit this style */
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
    display: flex;
    justify-content: center; /* Center the form itself within the fixed container */
}
div.stForm > div {
    display: flex;
    flex-direction: row; /* Ensure input and button are side-by-side */
    align-items: center;
    width: 100%;
    max-width: 760px; /* This ensures the form itself aligns with the max-width of input-field-wrapper */
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

# --- INPUT BAR (Fixed at bottom) --- #
st.markdown('<div class="input-box">', unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    # This column layout will be within the input-field-wrapper
    col1, col2 = st.columns([10, 1])
    with col1:
        # Wrap input in a div for consistent styling and to apply max-width
        st.markdown('<div class="input-field-wrapper">', unsafe_allow_html=True)
        user_input = st.text_input("Message", "", label_visibility="collapsed", key="input_text", placeholder="Type your message...")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        send = st.form_submit_button("➤", help="Send message")
        st.markdown("""
            <style>
                /* Specific styling for the send button */
                .stButton > button[kind="primary"] {
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
                    margin-left: 0; /* Adjust margin if needed */
                    padding: 0;
                }
                .stButton > button[kind="primary"]:hover {
                    background-color: #1a56c7;
                }
            </style>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# --- HANDLE SEND --- #
if send and user_input.strip():
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    response = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": response})

    user_message_count = len([m for m in active_chat["messages"] if m["role"] == "user"])
    if user_message_count == 3:
        rename_chat(active_id, active_chat["messages"][0]["content"][:30] + "...")

    st.rerun() # Rerun to display new messages
