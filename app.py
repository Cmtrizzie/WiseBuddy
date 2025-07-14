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
/* Base styling for the entire app */
body, .main, .block-container, [data-testid="stAppViewContainer"] {
    background-color: #000000 !important; /* Deep black background */
    color: white !important;
    font-family: 'Inter', sans-serif; /* Using Inter font for a modern look */
}

/* Hide Streamlit's default header and footer elements */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

/* Custom Header Styling */
.custom-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background-color: #000000;
    position: sticky; /* Keeps the header at the top when scrolling */
    top: 0;
    z-index: 1000;
    color: white;
    border-bottom: 1px solid #1a1a1a; /* Subtle border for separation */
}
.header-icon {
    font-size: 24px;
    cursor: pointer;
    padding: 5px;
    transition: color 0.2s ease;
}
.header-icon:hover {
    color: #999999; /* Lighten on hover */
}
.header-title {
    font-size: 18px;
    font-weight: 500;
}

/* Chat Message Container */
.chat-container {
    padding-bottom: 120px; /* Space for the fixed input bar at the bottom */
    padding-top: 20px; /* Space below the header */
    max-width: 800px; /* Max width for readability on large screens */
    margin: 0 auto; /* Center the chat container */
    padding-left: 15px; /* Padding for mobile */
    padding-right: 15px; /* Padding for mobile */
}
.message {
    max-width: 75%; /* Slightly wider message bubbles */
    padding: 12px 18px; /* More padding inside bubbles */
    border-radius: 22px; /* Slightly more rounded corners */
    margin: 10px 0;
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2); /* Subtle shadow for depth */
}
.user {
    background-color: #1a1a1a; /* Darker grey for user messages */
    margin-left: auto;
    text-align: right;
    border-bottom-right-radius: 8px; /* Asymmetrical rounding */
}
.bot {
    background-color: #282828; /* Slightly lighter grey for bot messages */
    margin-right: auto;
    text-align: left;
    border-bottom-left-radius: 8px; /* Asymmetrical rounding */
}

/* Welcome Message Styling */
.welcome-message {
    text-align: center;
    margin-top: 25vh; /* Vertically center initially */
    color: gray;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 20px; /* Ensure padding on small screens */
}
.welcome-message img {
    filter: drop-shadow(0 0 10px rgba(0, 150, 255, 0.4)); /* Glow effect for the emoji */
}
.welcome-message h3 {
    color: white;
    margin-top: 15px;
    margin-bottom: 5px;
    font-size: 26px; /* Slightly larger heading */
}
.welcome-message p {
    font-size: 17px; /* Slightly larger text */
    color: #aaaaaa;
}

/* --- Fixed Input Bar Styling (Creative Enhancements) --- */
.input-box {
    position: fixed; /* Keep it fixed at the bottom */
    bottom: 0;
    left: 0;
    right: 0;
    background: #000000; /* Match body background */
    padding: 15px 20px; /* Padding around the input field */
    border-top: 1px solid #1a1a1a; /* Subtle top border */
    z-index: 1000;
    display: flex;
    justify-content: center; /* Center the content */
    align-items: center; /* Vertically center content */
    box-shadow: 0 -2px 10px rgba(0,0,0,0.5); /* Shadow for lift-off effect */
}

.input-field-wrapper {
    display: flex;
    align-items: center;
    width: 100%;
    max-width: 760px; /* Max width for the input field to match chat container */
    background: #1f1f1f; /* Background for the input area itself */
    border-radius: 30px; /* Highly rounded corners */
    border: 1px solid #333333; /* A more prominent, but subtle border */
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3); /* Inner shadow for depth */
}
.input-field-wrapper:focus-within { /* Style when input is focused */
    border-color: #2563eb; /* Blue border on focus */
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3), 0 0 0 3px rgba(37, 99, 235, 0.3); /* Outer glow */
}

input[type="text"] {
    flex-grow: 1; /* Allows the text input to take available space */
    background: transparent; /* No background for the input element itself */
    border: none; /* No border */
    outline: none; /* No outline on focus */
    color: white; /* Text color */
    font-size: 16px;
    padding: 12px 15px; /* More padding inside the text input */
    line-height: 1.5; /* Ensure good line height */
}
input[type="text"]::placeholder {
    color: #888; /* Placeholder text color */
}

/* Styling for the Streamlit send button */
.stButton > button[kind="primary"] {
    background-color: #2563eb; /* Blue send button */
    color: white;
    border: none;
    border-radius: 50%; /* Circular button */
    width: 44px; /* Slightly larger button */
    height: 44px; /* Slightly larger button */
    font-size: 20px; /* Larger icon */
    display: flex;
    justify-content: center;
    align-items: center;
    margin-left: 8px; /* Space between input and button */
    padding: 0;
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.1s ease;
    flex-shrink: 0; /* Prevent shrinking */
    box-shadow: 0 2px 5px rgba(0,0,0,0.4); /* Shadow for the button */
}
.stButton > button[kind="primary"]:hover {
    background-color: #1a56c7; /* Darker blue on hover */
    transform: translateY(-1px); /* Slight lift effect */
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0); /* Press effect */
}

/* Hide the Streamlit default button styling for the form submit button */
div.stForm {
    width: 100%;
    margin-top: 0;
    margin-bottom: 0;
    display: flex;
    justify-content: center;
}
div.stForm > div {
    display: flex;
    flex-direction: row; /* Ensure input and button are side-by-side */
    align-items: center;
    width: 100%;
    max-width: 760px; /* This ensures the form itself aligns with the max-width of input-field-wrapper */
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

# --- INPUT BAR (Fixed at bottom with creative enhancements) --- #
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
        # The Streamlit button will inherit the custom styling defined in the <style> block
        send = st.form_submit_button("➤", help="Send message", type="primary") # type="primary" helps target it with CSS
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
