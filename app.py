import streamlit as st
import uuid
import google.generativeai as genai

# --- CONFIG --- #
st.set_page_config(page_title="WiseBuddy 🤖", layout="wide", initial_sidebar_state="collapsed") # Start collapsed

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
    st.rerun() # Rerun to display new chat

def switch_chat(chat_id):
    st.session_state.active_chat = chat_id
    st.rerun() # Rerun to display switched chat

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

/* --- HIDE ALL DEFAULT STREAMLIT HEADER ELEMENTS - MORE AGGRESSIVE --- */
/* Target specific data-testids used by Streamlit for its header/toolbar */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarHeader"], /* In case a sidebar header is showing */
/* Target the actual header HTML element within the app view */
[data-testid="stAppViewContainer"] > header,
.stApp > header {
    display: none !important;
    visibility: hidden !important; /* Extra measure to ensure it's gone */
    height: 0px !important; /* Collapse its height */
    padding: 0px !important; /* Remove any padding */
    margin: 0px !important; /* Remove any margin */
}

/* Ensure the main content block starts at the very top */
.block-container {
    padding-top: 0px !important;
    padding-left: 0px !important;
    padding-right: 0px !important;
}

/* Custom Header Styling - ENHANCED */
.custom-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px; /* Slightly less vertical padding, more horizontal */
    background-color: #000000;
    position: sticky; /* Keeps the header at the top when scrolling */
    top: 0;
    z-index: 1000;
    color: white;
    border-bottom: 1px solid #1a1a1a; /* Subtle border for separation */
}
.header-item { /* New class for clickable header items */
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px 12px; /* Increased padding for larger clickable area */
    border-radius: 10px; /* Slight rounding */
    cursor: pointer;
    transition: background-color 0.2s ease, color 0.2s ease;
    min-width: 44px; /* Ensure minimum touch target size */
    min-height: 44px; /* Ensure minimum touch target size */
    box-sizing: border-box; /* Include padding in width/height */
}
.header-item:hover {
    background-color: #1a1a1a; /* Subtle background on hover */
    color: #cccccc;
}
.header-icon {
    font-size: 24px;
}
.header-title {
    font-size: 18px;
    font-weight: 500;
    white-space: nowrap; /* Prevent "New chat" from wrapping */
    overflow: hidden;
    text-overflow: ellipsis; /* Add ellipsis for long titles */
    max-width: 150px; /* Limit width for title */
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

/* --- ST.CHAT_INPUT Styling (Crucial for the correct input bar) --- */
/* This targets the container for st.chat_input */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #000000; /* Match body background */
    padding: 15px 20px;
    border-top: 1px solid #1a1a1a;
    z-index: 1000;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.5); /* Shadow for lift-off effect */
    display: flex; /* Ensure its content is centered */
    justify-content: center; /* Center the input field itself */
    align-items: center;
}

/* Target the actual input field within st.chat_input */
[data-testid="stChatInput"] > div > label + div { /* Selects the div containing the text input and button */
    background: #1f1f1f; /* Background for the input area itself */
    border-radius: 30px; /* Highly rounded corners */
    border: 1px solid #333333; /* A more prominent, but subtle border */
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3); /* Inner shadow for depth */
    max-width: 760px; /* Max width for the input field to match chat container */
    width: 100%; /* Take full width within its flex container */
    padding: 0; /* Remove internal padding from streamlit's default */
}

/* Focus style for the input field */
[data-testid="stChatInput"] > div > label + div:focus-within {
    border-color: #2563eb; /* Blue border on focus */
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3), 0 0 0 3px rgba(37, 99, 235, 0.3); /* Outer glow */
}

/* Target the text input itself */
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: white !important;
    font-size: 16px !important;
    padding: 12px 15px !important; /* More padding inside the text input */
    line-height: 1.5 !important;
    resize: none !important; /* Prevent manual resizing */
}

/* Placeholder color */
[data-testid="stChatInput"] textarea::placeholder {
    color: #888 !important;
}

/* Target the send button within st.chat_input */
[data-testid="stChatInput"] button {
    background-color: #2563eb !important; /* Blue send button */
    color: white !important;
    border: none !important;
    border-radius: 50% !important; /* Circular button */
    width: 44px !important; /* Slightly larger button */
    height: 44px !important; /* Slightly larger button */
    min-width: 44px !important; /* Prevent it from shrinking */
    font-size: 20px !important; /* Larger icon */
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin-left: 8px !important; /* Space between input and button */
    padding: 0 !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease, transform 0.1s ease !important;
    flex-shrink: 0 !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.4) !important; /* Shadow for the button */
}
[data-testid="stChatInput"] button:hover {
    background-color: #1a56c7 !important; /* Darker blue on hover */
    transform: translateY(-1px) !important; /* Slight lift effect */
}
[data-testid="stChatInput"] button:active {
    transform: translateY(0) !important; /* Press effect */
}

/* Ensure no default Streamlit forms are interfering if not explicitly used */
div.stForm { display: none; }

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0d0d0d; /* Darker sidebar background */
    color: white;
    padding-top: 10px; /* Space from top */
}

[data-testid="stSidebar"] .stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 10px 15px;
    width: 100%;
    margin-bottom: 10px;
    font-size: 16px;
    transition: background-color 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #1a56c7;
}

.sidebar-chat-item {
    padding: 10px 15px;
    margin-bottom: 5px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    word-wrap: break-word;
}
.sidebar-chat-item:hover {
    background-color: #1a1a1a;
}
.sidebar-chat-item.active {
    background-color: #282828;
    border-left: 3px solid #2563eb;
    padding-left: 12px; /* Adjust for border */
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTENT --- #
with st.sidebar:
    st.markdown("## Chat History")
    if st.button("➕ Start New Chat", key="sidebar_new_chat_button"):
        new_chat()

    st.markdown("---") # Separator

    if st.session_state.chat_sessions:
        for chat_id, chat_data in st.session_state.chat_sessions.items():
            is_active = " active" if chat_id == st.session_state.active_chat else ""
            st.markdown(f"""
                <div class="sidebar-chat-item{is_active}" onclick="window.parent.document.querySelector('[data-testid=\"stSidebarUserContent\"]').click();
                                                                   fetch('/_st_internal_script_rerun?action=rerun&value={chat_id}')">
                    {chat_data['title']}
                </div>
            """, unsafe_allow_html=True)
            # Using a hidden st.button for actual switching (more reliable than JS for direct state change)
            if st.button(chat_data['title'], key=f"switch_chat_{chat_id}", help="Switch to this chat", use_container_width=True):
                switch_chat(chat_id)
                # Note: The JS click on sidebar content is an attempt to close sidebar after click,
                # but might not work perfectly with Streamlit's internal mechanisms.
                # Direct st.button is the reliable way.
    else:
        st.markdown("<p style='color: #888;'>No chats yet. Start a new one!</p>")


# --- CUSTOM HEADER (Including functionality) --- #
st.markdown(f"""
<div class="custom-header">
    <div class="header-item" onclick="window.parent.document.querySelector('[data-testid=\"stSidebar\"] button').click()">
        <div class="header-icon">☰</div>
    </div>
    <div class="header-item">
        <div class="header-title">{active_chat["title"]}</div>
    </div>
    <div class="header-item" onclick="streamlit.setComponentValue('new_chat_clicked', true)">
        <div class="header-icon">+</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Streamlit component for new chat button to capture click
if st.session_state.get('new_chat_clicked', False):
    new_chat()
    st.session_state['new_chat_clicked'] = False # Reset click state

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
if user_input: # st.chat_input returns the message if entered, None otherwise
    active_chat["messages"].append({"role": "user", "content": user_input.strip()})
    response = generate_reply(user_input.strip())
    active_chat["messages"].append({"role": "assistant", "content": response})

    user_message_count = len([m for m in active_chat["messages"] if m["role"] == "user"])
    # Rename chat after 3 user messages if it's still "New Chat"
    if user_message_count == 3 and active_chat["title"] == "New Chat":
        # Use a short snippet of the first user message as the title
        rename_chat(active_id, active_chat["messages"][0]["content"][:30].strip() + "...")

    st.rerun() # Rerun to display new messages and potentially updated title
