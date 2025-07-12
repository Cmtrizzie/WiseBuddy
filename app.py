import streamlit as st
import random
import time
from datetime import datetime

# --- Constants ---
SESSION_STATE_CHATS = "chats"
SESSION_STATE_CURRENT_CHAT_ID = "current_chat_id"
SESSION_STATE_LAST_MESSAGE_TIME = "last_message_time" # To prevent rapid re-runs on input

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Chat App",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
def load_custom_css():
    st.markdown("""
    <style>
        /* General body styling */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f6; /* Light grey background */
        }

        /* Streamlit main content area */
        .stApp {
            background-color: #f0f2f6;
        }

        /* Sidebar styling */
        .st-emotion-cache-vk3305 { /* Target the sidebar container */
            background-color: #ffffff; /* White background for sidebar */
            border-right: 1px solid #e0e0e0;
            padding-top: 20px;
        }
        .st-emotion-cache-vk3305 .st-emotion-cache-1f1963o { /* Adjust padding for sidebar content */
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .st-emotion-cache-vk3305 h1 { /* Sidebar title */
            color: #333333;
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-left: 1rem;
        }

        /* Conversation items */
        .conversation-item {
            padding: 12px 15px;
            margin: 6px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            font-size: 15px;
            color: #555555;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .conversation-item:hover {
            background-color: #f0f2f6; /* Lighter hover background */
            color: #333333;
        }
        
        .conversation-item.active {
            background-color: #e6f2ff; /* Light blue for active */
            border-left: 4px solid #007bff; /* Primary blue border */
            color: #007bff;
            font-weight: 600;
        }
        .conversation-item.active .conversation-icon {
            color: #007bff;
        }

        /* New Chat button */
        .new-chat-button {
            width: 100%;
            padding: 12px;
            margin-top: 20px;
            background-color: #007bff; /* Primary blue */
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .new-chat-button:hover {
            background-color: #0056b3; /* Darker blue on hover */
        }

        /* Profile section */
        .profile-section {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 20%; /* Matches sidebar width */
            padding: 15px 20px;
            background: #ffffff;
            border-top: 1px solid #e0e0e0;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05); /* Subtle shadow */
            z-index: 1000; /* Ensure it stays on top */
        }
        
        .profile-content {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .profile-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: #6c757d; /* Grey for avatar */
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
            flex-shrink: 0; /* Prevent shrinking */
        }
        
        /* Main chat area styling */
        .main-chat-container {
            background-color: #ffffff; /* White background for chat messages */
            border-radius: 12px;
            padding: 20px;
            margin: 20px auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); /* More prominent shadow */
            max-width: 900px; /* Max width for readability */
            min-height: 70vh; /* Minimum height for chat area */
            display: flex;
            flex-direction: column;
        }
        .message-list {
            flex-grow: 1;
            overflow-y: auto; /* Enable scrolling for messages */
            padding-right: 15px; /* Space for scrollbar */
            margin-bottom: 20px;
        }

        /* Message bubbles */
        .st-emotion-cache-1c7y2qn { /* Target chat message container */
            background-color: transparent !important;
            padding: 0 !important;
            margin-bottom: 15px;
        }

        .st-emotion-cache-1c7y2qn .st-emotion-cache-1v0mbvd { /* Target the message content div */
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 75%; /* Limit message width */
            word-wrap: break-word;
            font-size: 15px;
            line-height: 1.5;
            position: relative;
        }

        /* User message */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(2) > div { /* User message content */
            background-color: #e0f2f7; /* Light blue for user */
            color: #333333;
            margin-left: auto; /* Align to right */
            border-bottom-right-radius: 4px; /* Sharpen corner towards avatar */
        }
        /* User avatar */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:first-child {
            order: 2; /* Move avatar to right for user */
        }
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child {
            flex-direction: row-reverse; /* Reverse direction for user message */
        }

        /* Assistant message */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(1) > div { /* Assistant message content */
            background-color: #f8f9fa; /* Off-white for assistant */
            color: #333333;
            margin-right: auto; /* Align to left */
            border-bottom-left-radius: 4px; /* Sharpen corner towards avatar */
        }

        /* Timestamps */
        .message-time {
            font-size: 0.7rem;
            color: #999999;
            margin-top: 5px;
            text-align: right; /* Align timestamp with message bubble */
            padding-right: 5px; /* Small padding */
        }
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(2) .message-time {
            text-align: right; /* User message timestamp */
        }
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(1) .message-time {
            text-align: left; /* Assistant message timestamp */
        }

        /* Chat input */
        .st-emotion-cache-1oe5f0g { /* Target the chat input container */
            padding: 15px 20px;
            background-color: #ffffff;
            border-top: 1px solid #e0e0e0;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
            border-radius: 12px;
            margin-top: 20px;
        }
        .st-emotion-cache-1oe5f0g input {
            border-radius: 25px;
            padding: 10px 20px;
            border: 1px solid #cccccc;
            box-shadow: none;
        }
        .st-emotion-cache-1oe5f0g button {
            background-color: #007bff;
            border-radius: 25px;
            padding: 10px 15px;
        }
        .st-emotion-cache-1oe5f0g button:hover {
            background-color: #0056b3;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        /* Loading spinner */
        .stSpinner > div > div {
            border-top-color: #007bff !important;
        }

        /* Hide specific Streamlit form submit buttons */
        /* Targets the hidden "New Chat" submit button */
        [data-testid="stFormSubmitButton-Create New Chat Hidden"] {
            display: none !important;
        }
        /* Targets all hidden "Switch to" submit buttons */
        [data-testid^="stFormSubmitButton-Switch to "] {
            display: none !important;
        }

    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
def initialize_session_state():
    if SESSION_STATE_CHATS not in st.session_state:
        # Structure: {chat_id: {"title": "...", "messages": [...]}}
        st.session_state[SESSION_STATE_CHATS] = {
            "chat_1": {"title": "AI Ethics Discussion", "messages": []},
            "chat_2": {"title": "Project X Summary", "messages": []},
            "chat_3": {"title": "Quantum Physics Learning", "messages": []},
        }
        # Add an initial message to one of the chats for demonstration
        st.session_state[SESSION_STATE_CHATS]["chat_1"]["messages"].append({
            "role": "assistant",
            "content": "Hello! How can I assist you with AI Ethics today?",
            "time": datetime.now().strftime("%H:%M")
        })

    if SESSION_STATE_CURRENT_CHAT_ID not in st.session_state:
        st.session_state[SESSION_STATE_CURRENT_CHAT_ID] = "chat_1" # Default to the first chat

    if SESSION_STATE_LAST_MESSAGE_TIME not in st.session_state:
        st.session_state[SESSION_STATE_LAST_MESSAGE_TIME] = None

# --- Helper Functions ---
def generate_chat_id():
    return f"chat_{int(time.time() * 1000)}_{random.randint(100, 999)}"

def switch_chat(chat_id):
    st.session_state[SESSION_STATE_CURRENT_CHAT_ID] = chat_id
    # Clear the chat input if any, to prevent old input from reappearing
    st.session_state.chat_input_key = "" # This will reset the input widget
    st.rerun()

def create_new_chat():
    new_chat_id = generate_chat_id()
    st.session_state[SESSION_STATE_CHATS][new_chat_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state[SESSION_STATE_CURRENT_CHAT_ID] = new_chat_id
    st.rerun()

# --- Render Functions ---
def render_sidebar():
    with st.sidebar:
        st.title("Chats")

        # New Chat button (custom HTML for styling, triggers hidden Streamlit form button)
        st.markdown(
            f'<button class="new-chat-button" onclick="window.parent.document.querySelector(\'[data-testid="stFormSubmitButton-Create New Chat Hidden"]\').click();">'
            f'<span style="font-size: 1.2em;">+</span> New Chat'
            f'</button>',
            unsafe_allow_html=True
        )
        # Hidden form to trigger the new chat creation
        with st.form("new_chat_form", clear_on_submit=True):
            st.form_submit_button(
                "Create New Chat Hidden",
                on_click=create_new_chat,
                type="primary",
                help="This button is hidden and triggered by the custom HTML button above."
            )

        st.markdown("<div style='margin-top: 20px; border-top: 1px solid #f0f0f0;'></div>", unsafe_allow_html=True)

        # Conversation history list
        chat_ids = list(st.session_state[SESSION_STATE_CHATS].keys())
        chat_ids.sort(key=lambda x: (x != st.session_state[SESSION_STATE_CURRENT_CHAT_ID], x), reverse=False)

        for conv_id in chat_ids:
            title = st.session_state[SESSION_STATE_CHATS][conv_id]["title"]
            is_active = conv_id == st.session_state[SESSION_STATE_CURRENT_CHAT_ID]
            icon = "💬" if not is_active else "✨"

            # Each conversation item will be a form to trigger the switch
            with st.form(f"chat_switch_form_{conv_id}", clear_on_submit=True):
                st.markdown(
                    f'<div class="conversation-item {"active" if is_active else ""}" '
                    f'onclick="window.parent.document.querySelector(\'[data-testid^=\"stFormSubmitButton\"]\', this.parentNode).click();">' # Target submit button within THIS form
                    f'<span class="conversation-icon">{icon}</span> {title}'
                    '</div>',
                    unsafe_allow_html=True
                )
                # Hidden submit button for this form
                st.form_submit_button(
                    f"Switch to {title} (Hidden)", # The label is part of the data-testid
                    key=f"switch_chat_submit_{conv_id}", # Unique key for the submit button
                    on_click=switch_chat,
                    args=(conv_id,),
                    # No need for unsafe_allow_html=True here, as it's a standard button
                )


        # Fixed profile section at bottom
        st.markdown(
            """
            <div class="profile-section">
                <div class="profile-content">
                    <div class="profile-avatar">U</div>
                    <div>
                        <div style="font-weight: bold; color: #333;">User</div>
                        <div style="font-size: 0.8rem; color: #666;">Active now</div>
                    </div>
                </div>
                <div style="margin-top: 10px; font-size: 0.75rem; color: #999;">
                    Chat ID: <span style="font-family: monospace;">""" + st.session_state[SESSION_STATE_CURRENT_CHAT_ID] + """</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_main_chat_area():
    current_chat_id = st.session_state[SESSION_STATE_CURRENT_CHAT_ID]
    current_chat_title = st.session_state[SESSION_STATE_CHATS][current_chat_id]["title"]
    messages = st.session_state[SESSION_STATE_CHATS][current_chat_id]["messages"]

    st.title(current_chat_title)

    # Use a container for messages to allow scrolling
    message_container = st.container()
    with message_container:
        # Display chat messages
        for message in messages:
            with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])
                st.markdown(f'<div class="message-time">{message["time"]}</div>', unsafe_allow_html=True)

    # Chat input
    # Ensure a unique key for the chat input to allow clearing it
    chat_input_key = "chat_input_key"
    if chat_input_key not in st.session_state:
        st.session_state[chat_input_key] = ""

    prompt = st.chat_input("Type your message...", key=chat_input_key)

    if prompt and prompt != st.session_state[SESSION_STATE_LAST_MESSAGE_TIME]:
        st.session_state[SESSION_STATE_LAST_MESSAGE_TIME] = prompt # Store the last prompt to prevent re-processing on rerun

        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state[SESSION_STATE_CHATS][current_chat_id]["messages"].append({
            "role": "user",
            "content": prompt,
            "time": timestamp
        })

        # Update conversation title if first message in this chat
        if len(st.session_state[SESSION_STATE_CHATS][current_chat_id]["messages"]) == 1:
            st.session_state[SESSION_STATE_CHATS][current_chat_id]["title"] = prompt[:25] + ("..." if len(prompt) > 25 else "")

        # Display user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            st.markdown(f'<div class="message-time">{timestamp}</div>', unsafe_allow_html=True)

        # Generate bot response with spinner
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                time.sleep(random.uniform(0.5, 1.5)) # Simulate processing time
                response_container = st.empty()
                simulated_response = f"I understand you're asking about '{prompt}'. Here's what I can share about it, based on my current knowledge. This is a simulated response to demonstrate the chat functionality and improved UI."

                # Simulated typing effect
                full_response = ""
                for word in simulated_response.split():
                    full_response += word + " "
                    response_container.markdown(full_response + "▌") # Typing cursor
                    time.sleep(0.05) # Faster typing
                response_container.markdown(full_response) # Final message without cursor

            timestamp = datetime.now().strftime("%H:%M")
            st.markdown(f'<div class="message-time">{timestamp}</div>', unsafe_allow_html=True)

            st.session_state[SESSION_STATE_CHATS][current_chat_id]["messages"].append({
                "role": "assistant",
                "content": full_response,
                "time": timestamp
            })

        # Rerun to update the chat history display immediately after bot response
        st.rerun()

# --- Main Application Flow ---
if __name__ == "__main__":
    load_custom_css()
    initialize_session_state()

    render_sidebar()
    render_main_chat_area()

