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
    cursor: pointer; /* Ensure pointer cursor for visual feedback */
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

.sidebar-chat-item-container {
    margin-bottom: 5px;
}
.sidebar-chat-item {
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    word-wrap: break-word;
    color: white; /* Ensure text color is white */
}
.sidebar-chat-item:hover {
    background-color: #1a1a1a;
}
.sidebar-chat-item.active {
    background-color: #282828;
    border-left: 3px solid #2563eb;
    padding-left: 12px; /* Adjust for border */
}

/* IMPORTANT: Hidden buttons for JS interaction. This makes them truly invisible. */
[data-testid^="stButton-hidden_"] { /* Target all buttons whose data-testid starts with 'stButton-hidden_' */
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    position: absolute !important;
    overflow: hidden !important;
    pointer-events: none !important; /* Ensure they don't capture any pointer events */
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTENT --- #
with st.sidebar:
    st.markdown("## Chat History")
    if st.button("➕ Start New Chat", key="sidebar_new_chat_button", use_container_width=True):
        new_chat()

    st.markdown("---") # Separator

    if st.session_state.chat_sessions:
        # Sort chats to ensure consistent display, e.g., by modification time or UUID
        # For simplicity, sorting by title for now if it's already a string.
        sorted_chat_ids = sorted(st.session_state.chat_sessions.keys(),
                                 key=lambda x: st.session_state.chat_sessions[x].get('last_updated', x),
                                 reverse=True) # Assuming 'last_updated' key exists for sorting

        for chat_id in sorted_chat_ids:
            chat_data = st.session_state.chat_sessions[chat_id]
            is_active = " active" if chat_id == st.session_state.active_chat else ""

            # Use a regular Streamlit button for each chat item
            if st.button(
                chat_data['title'],
                key=f"sidebar_chat_select_{chat_id}",
                help="Switch to this chat",
                use_container_width=True
            ):
                switch_chat(chat_id)
                # Attempt to close sidebar after switching
                # This direct JS might still be a bit flaky on mobile
                st.markdown("""
                    <script>
                        // Use a short delay to ensure the DOM is ready for the click
                        setTimeout(function() {
                            const sidebarToggleButton = window.parent.document.querySelector('[data-testid="stSidebarToggleButton"]');
                            if (sidebarToggleButton) {
                                sidebarToggleButton.click();
                                // console.log("Sidebar toggle button clicked after chat switch.");
                            } else {
                                // console.warn("Sidebar toggle button not found after chat switch.");
                            }
                        }, 100); // Increased delay slightly
                    </script>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #888;'>No chats yet. Start a new one!</p>")

# --- HIDDEN STREAMLIT BUTTONS FOR HEADER INTERACTIVITY ---
# These buttons are not visible but will capture clicks triggered by our custom HTML
# We assign them unique keys. Streamlit will assign a data-testid like "stButton-KEY_NAME"
hidden_sidebar_toggle_btn = st.button("Toggle Sidebar", key="hidden_sidebar_toggle_button")
hidden_new_chat_btn = st.button("New Chat Action", key="hidden_new_chat_button_action")
hidden_chat_title_btn = st.button("Chat Title Action", key="hidden_chat_title_button_action")


# --- Custom Header HTML with inline JavaScript to trigger hidden buttons ---
# Fixed: Doubled curly braces for JavaScript template literal expressions within the f-string
st.markdown(f"""
<div class="custom-header">
    <div class="header-item" id="header-sidebar-toggle">
        <div class="header-icon">☰</div>
    </div>
    <div class="header-item" id="header-chat-title">
        <div class="header-title">{active_chat["title"]}</div>
    </div>
    <div class="header-item" id="header-new-chat-button">
        <div class="header-icon">+</div>
    </div>
</div>

<script>
    // Execute this script only when the DOM is fully loaded to ensure elements exist
    document.addEventListener('DOMContentLoaded', function() {{
        // Helper function to attach event listeners
        function setupClickListener(elementId, targetButtonDataTestId) {{
            const customElement = document.getElementById(elementId);
            if (customElement) {{
                // console.log(`Attempting to set up listener for ${{elementId}}`);

                // Listener for general clicks (desktop browsers)
                customElement.addEventListener('click', function(event) {{
                    event.stopPropagation(); // Prevent event from bubbling up to parent elements
                    event.preventDefault(); // Prevent default browser actions
                    // console.log(`Custom element ${{elementId}} clicked.`);
                    triggerHiddenStreamlitButton(targetButtonDataTestId);
                }});

                // Listener for touch events (mobile phones)
                customElement.addEventListener('touchend', function(event) {{
                    event.stopPropagation(); // Prevent event from bubbling up
                    event.preventDefault(); // Prevent default browser actions (e.g., zoom)
                    // console.log(`Custom element ${{elementId}} touched (touchend).`);
                    triggerHiddenStreamlitButton(targetButtonDataTestId);
                }});
            }} else {{
                console.error(`Custom element with ID ${{elementId}} not found.`);
            }}
        }}

        // Function to programmatically click the hidden Streamlit button
        function triggerHiddenStreamlitButton(dataTestId) {{
            // Use setTimeout to give Streamlit's rendering a moment to ensure the button is active
            setTimeout(function() {{
                // Streamlit buttons are within a div with data-testid, and the actual <button> is a child
                const targetButton = window.parent.document.querySelector(`[data-testid="${{dataTestId}}"] > button`);
                if (targetButton) {{
                    targetButton.click(); // Programmatically click the hidden button
                    // console.log(`Hidden Streamlit button ${{dataTestId}} clicked.`);
                }} else {{
                    console.error(`Target Streamlit button with data-testid="${{dataTestId}}" not found.`);
                }}
            }}, 50); // Small delay, adjust if needed (e.g., 100ms)
        }}

        // Setup listeners for each header item, mapping to their respective hidden Streamlit buttons
        setupClickListener('header-sidebar-toggle', 'stButton-hidden_sidebar_toggle_button');
        setupClickListener('header-new-chat-button', 'stButton-hidden_new_chat_button_action');
        setupClickListener('header-chat-title', 'stButton-hidden_chat_title_button_action');

    }}); // End DOMContentLoaded
</script>
""", unsafe_allow_html=True)


# --- Python logic triggered by hidden buttons ---
# These conditions will be true if the corresponding hidden button was clicked by JS
if hidden_sidebar_toggle_btn:
    # Streamlit's native sidebar toggle logic handles itself.
    # No explicit `st.sidebar.expanded = ...` needed here.
    st.info("Sidebar toggled via header button!") # For debugging feedback

if hidden_new_chat_btn:
    new_chat() # Call the new_chat function
    st.info("New chat created via header button!") # For debugging feedback

if hidden_chat_title_btn:
    # This is where you'd add logic for what happens when the title is clicked
    st.toast(f"You clicked on the chat title: '{active_chat['title']}'", icon="ℹ️")


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

    # Update 'last_updated' timestamp for sorting in sidebar
    # Using a new UUID for chronological order (or datetime.now())
    active_chat['last_updated'] = str(uuid.uuid4())

    user_message_count = len([m for m in active_chat["messages"] if m["role"] == "user"])
    # Rename chat after 3 user messages if it's still "New Chat"
    if user_message_count == 3 and active_chat["title"] == "New Chat":
        # Use a short snippet of the first user message as the title
        rename_chat(active_id, active_chat["messages"][0]["content"][:30].strip() + "...")

    st.rerun() # Rerun to display new messages and potentially updated title
