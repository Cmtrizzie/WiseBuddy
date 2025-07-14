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
        "title": "New Chat", # Default title for a new chat
        "messages": []
    }
    st.session_state.active_chat = chat_id
    st.rerun() # Rerun to update the display

def rename_chat(chat_id, title):
    st.session_state.chat_sessions[chat_id]["title"] = title

def generate_reply(user_input):
    try:
        # In a real app, you'd start a chat session with the model
        # and send messages to it. For this example, we'll just simulate.
        # Assuming `model` is already configured for Gemini 1.5 Pro
        chat_session = model.start_chat(history=active_chat["messages"])
        response = chat_session.send_message(user_input)
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

/* --- HIDE ALL DEFAULT STREAMLIT HEADER ELEMENTS - MORE AGGRESSIVE --- */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarHeader"],
[data-testid="stAppViewContainer"] > header,
.stApp > header,
/* This targets the three-dots menu button and the sidebar toggle button if they persist */
.css-1rs6os.ets6coq3, /* Specific class for the menu button, might change */
.st-emotion-cache-s8w6x2 { /* Another common Streamlit header/menu element */
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
}

/* Ensure the main content block starts at the very top */
.block-container {
    padding-top: 0px !important;
    padding-left: 0px !important;
    padding-right: 0px !important;
}

/* Custom Header Styling - ENHANCED FOR INTERACTIVITY */
.custom-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background-color: #000000;
    position: sticky;
    top: 0;
    z-index: 1000;
    color: white;
    border-bottom: 1px solid #1a1a1a;
    width: 100%; /* Ensure it spans full width */
    box-sizing: border-box; /* Include padding in width */
}

/* Streamlit buttons inside the header columns */
.st-emotion-cache-eczf16 { /* This is a common class for Streamlit's col/div containing buttons */
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0px; /* Remove default padding from column wrapper */
}
.stButton > button {
    background: none !important; /* Transparent background */
    border: none !important; /* No border */
    color: white !important; /* White icon/text color */
    font-size: 24px; /* Icon size */
    padding: 8px 12px !important; /* Larger clickable area */
    border-radius: 10px !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease, color 0.2s ease !important;
    min-width: 44px !important; /* Minimum touch target */
    height: 44px !important; /* Minimum touch target */
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
.stButton > button:hover {
    background-color: #1a1a1a !important; /* Subtle background on hover */
    color: #cccccc !important;
}
.stButton > button:focus:not(:active) {
    box-shadow: none !important; /* Remove focus outline */
}

/* Style for the dynamically updated title in the center */
.header-title-display {
    flex-grow: 1; /* Allows it to take available space */
    text-align: center;
    font-size: 18px;
    font-weight: 500;
    color: white;
    padding: 8px 0; /* Align with button padding */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis; /* Handle long titles */
}


/* Chat Message Container */
.chat-container {
    padding-bottom: 120px;
    padding-top: 20px;
    max-width: 800px;
    margin: 0 auto;
    padding-left: 15px;
    padding-right: 15px;
}
.message {
    max-width: 75%;
    padding: 12px 18px;
    border-radius: 22px;
    margin: 10px 0;
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.user {
    background-color: #1a1a1a;
    margin-left: auto;
    text-align: right;
    border-bottom-right-radius: 8px;
}
.bot {
    background-color: #282828;
    margin-right: auto;
    text-align: left;
    border-bottom-left-radius: 8px;
}

/* Welcome Message Styling */
.welcome-message {
    text-align: center;
    margin-top: 25vh;
    color: gray;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 20px;
}
.welcome-message img {
    filter: drop-shadow(0 0 10px rgba(0, 150, 255, 0.4));
}
.welcome-message h3 {
    color: white;
    margin-top: 15px;
    margin-bottom: 5px;
    font-size: 26px;
}
.welcome-message p {
    font-size: 17px;
    color: #aaaaaa;
}

/* --- ST.CHAT_INPUT Styling --- */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #000000;
    padding: 15px 20px;
    border-top: 1px solid #1a1a1a;
    z-index: 1000;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}

[data-testid="stChatInput"] > div > label + div {
    background: #1f1f1f;
    border-radius: 30px;
    border: 1px solid #333333;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
    max-width: 760px;
    width: 100%;
    padding: 0;
}

[data-testid="stChatInput"] > div > label + div:focus-within {
    border-color: #2563eb;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3), 0 0 0 3px rgba(37, 99, 235, 0.3);
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: white !important;
    font-size: 16px !important;
    padding: 12px 15px !important;
    line-height: 1.5 !important;
    resize: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #888 !important;
}

[data-testid="stChatInput"] button {
    background-color: #2563eb !important;
    color: white !important;
    border: none !important;
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    font-size: 20px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin-left: 8px !important;
    padding: 0 !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease, transform 0.1s ease !important;
    flex-shrink: 0 !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatInput"] button:hover {
    background-color: #1a56c7 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stChatInput"] button:active {
    transform: translateY(0) !important;
}

/* Ensure no default Streamlit forms are interfering if not explicitly used */
div.stForm { display: none; }

</style>
""", unsafe_allow_html=True)

# --- CUSTOM HEADER WITH INTERACTIVITY --- #
# Using st.columns to lay out the header items
header_cols = st.columns([1, 3, 1]) # Column ratios for left icon, title, right icon

with header_cols[0]:
    # Use st.button for the hamburger icon
    # Streamlit automatically adds a sidebar toggle when st.sidebar is used.
    # This button doesn't directly open it, but serves as a visual placeholder/trigger.
    # You'll need to enable the sidebar in the config (initial_sidebar_state)
    # or rely on the default toggle appearing if you want a clickable icon.
    # For a completely custom open/close, it requires JavaScript/advanced CSS.
    st.button("☰", key="menu_button", help="Open menu")

with header_cols[1]:
    # Display the current chat title dynamically
    st.markdown(f'<div class="header-title-display">{active_chat["title"]}</div>', unsafe_allow_html=True)

with header_cols[2]:
    # Use st.button for the new chat (+) icon
    if st.button("+", key="new_chat_button", help="Start a new chat"):
        new_chat() # Call the new_chat function

# --- SIDEBAR (appears from left) --- #
with st.sidebar:
    st.markdown("## WiseBuddy Menu")
    st.write("---")
    st.button("New Chat", on_click=new_chat) # Sidebar new chat button
    st.write("---")
    st.markdown("### Chat History")
    # Display existing chat sessions
    for chat_id, chat_data in st.session_state.chat_sessions.items():
        if st.button(chat_data["title"], key=f"sidebar_chat_{chat_id}"):
            st.session_state.active_chat = chat_id
            st.rerun() # Rerun to switch to the selected chat

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

# --- ST.CHAT_INPUT FOR MESSAGING --- #
user_input = st.chat_input("Type your message...")

# --- HANDLE SEND --- #
if user_input:
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    response = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": response})

    # Rename chat after 3 user messages (or based on first message, etc.)
    user_message_count = len([m for m in active_chat["messages"] if m["role"] == "user"])
    if user_message_count == 1 and active_chat["title"] == "New Chat": # Rename only on first user message
        rename_chat(active_id, active_chat["messages"][0]["content"][:30] + "...")
    st.rerun()
