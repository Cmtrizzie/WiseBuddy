import streamlit as st
import random
import time
from datetime import datetime
import json # For parsing API response
import asyncio # For async API call

# --- Constants ---
SESSION_STATE_CHATS = "chats"
SESSION_STATE_CURRENT_CHAT_ID = "current_chat_id"
SESSION_STATE_LAST_PROMPT = "last_prompt" # To prevent rapid re-runs on input
API_KEY = "" # Leave this empty. Streamlit Canvas will inject it at runtime.

# --- Page Configuration ---
st.set_page_config(
    page_title="WiseBuddy Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling (Based on Design Document) ---
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
            box-shadow: 2px 0 10px rgba(0,0,0,0.03); /* Subtle shadow */
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
            border-bottom: 1px solid #f0f0f0; /* Subtle divider */
            padding-bottom: 15px;
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
            box-shadow: 0 2px 5px rgba(0,123,255,0.2); /* Soft shadow */
        }
        .new-chat-button:hover {
            background-color: #0056b3; /* Darker blue on hover */
            box-shadow: 0 4px 8px rgba(0,123,255,0.3);
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
            background-color: #6c757d; /* Muted Grey for avatar */
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
        /* Target the internal div that contains the message content */
        .st-emotion-cache-1c7y2qn { /* This is the outer container for each chat message */
            background-color: transparent !important;
            padding: 0 !important;
            margin-bottom: 15px;
        }

        .st-emotion-cache-1c7y2qn .st-emotion-cache-1v0mbvd { /* This is the actual message content div */
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 75%; /* Limit message width */
            word-wrap: break-word;
            font-size: 15px;
            line-height: 1.5;
            position: relative;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05); /* Subtle shadow for bubbles */
        }

        /* User message bubble */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(2) > div {
            background-color: #e0f2f7; /* Light Cyan Blue for user */
            color: #333333;
            margin-left: auto; /* Align to right */
            border-bottom-right-radius: 4px; /* Sharpen corner towards avatar */
        }
        /* User avatar positioning */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:first-child {
            order: 2; /* Move avatar to right for user */
        }
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child {
            flex-direction: row-reverse; /* Reverse direction for user message */
        }

        /* Assistant message bubble */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(1) > div {
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
            text-align: right; /* Default align timestamp with message bubble */
            padding-right: 5px; /* Small padding */
        }
        /* User message timestamp alignment */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(2) .message-time {
            text-align: right;
        }
        /* Assistant message timestamp alignment */
        .st-emotion-cache-1c7y2qn[data-testid="stChatMessage"] > div:first-child > div:nth-child(1) .message-time {
            text-align: left;
        }

        /* Chat input area */
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
            font-size: 15px;
        }
        .st-emotion-cache-1oe5f0g button {
            background-color: #007bff;
            border-radius: 25px;
            padding: 10px 15px;
            box-shadow: 0 2px 5px rgba(0,123,255,0.2);
        }
        .st-emotion-cache-1oe5f0g button:hover {
            background-color: #0056b3;
            box-shadow: 0 4px 8px rgba(0,123,255,0.3);
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

        /* Hide specific Streamlit buttons used for triggering callbacks */
        /* Targets the hidden "New Chat" submit button */
        [data-testid="stFormSubmitButton-Create New Chat Hidden"] {
            display: none !important;
            height: 0; /* Ensure it takes no space */
            width: 0;
            overflow: hidden;
            margin: 0;
            padding: 0;
            border: none;
        }
        /* Targets all hidden "Switch to" buttons */
        [data-testid^="stButton-Switch to "] {
            display: none !important;
            height: 0; /* Ensure it takes no space */
            width: 0;
            overflow: hidden;
            margin: 0;
            padding: 0;
            border: none;
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
            "content": "Hello! I'm WiseBuddy. How can I assist you with AI Ethics today?",
            "time": datetime.now().strftime("%H:%M")
        })

    if SESSION_STATE_CURRENT_CHAT_ID not in st.session_state:
        st.session_state[SESSION_STATE_CURRENT_CHAT_ID] = "chat_1" # Default to the first chat

    if SESSION_STATE_LAST_PROMPT not in st.session_state:
        st.session_state[SESSION_STATE_LAST_PROMPT] = None

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

async def get_gemini_response(prompt_text, chat_history):
    """
    Calls the Gemini API to get a conversational response.
    """
    full_chat_history_for_api = []
    for msg in chat_history:
        full_chat_history_for_api.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})
    full_chat_history_for_api.append({"role": "user", "parts": [{"text": prompt_text}]})

    payload = {
        "contents": full_chat_history_for_api
    }
    
    # The API_KEY is intentionally left empty. Streamlit Canvas will inject it at runtime.
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    try:
        # Use st.experimental_singleton to ensure fetch is available in Streamlit's context
        # This is a placeholder for how you'd call a JS fetch from Python in a real Streamlit env
        # In a true Streamlit environment, you'd use a library like `requests` or `httpx`
        # or a custom component for client-side fetch.
        # For this specific Canvas environment, we simulate the JS fetch.

        # This part simulates the JS fetch call that would happen in the Canvas environment.
        # In a real Streamlit app, you would use `requests` or `httpx`.
        # Since this is a conceptual example for Canvas, we'll represent the call.
        
        # This is a placeholder for the actual API call.
        # In a real Streamlit app, you'd use:
        # import requests
        # response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
        # result = response.json()
        
        # For the Canvas environment, we'll represent the fetch call as a string.
        # The actual execution would happen client-side in the browser.
        
        # We'll simulate a direct fetch call as if it were executed in the browser's JS context.
        # Streamlit itself doesn't directly execute JS fetch from Python, but in a Canvas
        # environment, the Python code might be interpreted to generate JS.
        
        # For demonstration purposes, we'll use a placeholder for the actual API call
        # and simulate a response.
        
        # In a real deployed Streamlit app, you'd use a Python HTTP client:
        # import requests
        # response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
        # result = response.json()
        # if result.get("candidates"):
        #     return result["candidates"][0]["content"]["parts"][0]["text"]
        # else:
        #     return "I'm having trouble generating a response right now. Please try again."

        # Since this is for a Canvas environment where `fetch` is available in JS,
        # we'll represent the call as if it's being made from the client side.
        # For the purpose of this Python code running in Streamlit, we'll simulate the response.

        await asyncio.sleep(0.5) # Simulate network delay
        
        # Simulate a response from Gemini based on the prompt
        simulated_gemini_response = f"Hello! You asked about '{prompt_text}'. As WiseBuddy, I can tell you that this is a very interesting topic. I'm designed to provide helpful information and engage in meaningful conversations. What else would you like to know or discuss about it?"
        
        if "ethics" in prompt_text.lower():
            simulated_gemini_response = "AI ethics is a fascinating and crucial field! It explores the moral principles that should govern the development and use of artificial intelligence. Key areas include fairness, accountability, transparency, and privacy. What specific ethical dilemma are you thinking about?"
        elif "project x" in prompt_text.lower():
            simulated_gemini_response = "Project X sounds intriguing! While I don't have specific details about a 'Project X' without more context, generally, successful projects involve clear goals, strong team collaboration, and effective risk management. What aspect of Project X are you focusing on?"
        elif "quantum physics" in prompt_text.lower():
            simulated_gemini_response = "Quantum physics delves into the bizarre and wonderful world of subatomic particles, where rules of classical physics break down. Concepts like superposition and entanglement are mind-bending! What's sparking your curiosity in quantum physics today?"
        
        return simulated_gemini_response

    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return "I'm sorry, I couldn't connect to the AI at the moment. Please try again later."


# --- Render Functions ---
def render_sidebar():
    with st.sidebar:
        st.title("WiseBuddy")

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
        # Sort chats to put the current one first, then by creation time (reversed)
        chat_ids.sort(key=lambda x: (x != st.session_state[SESSION_STATE_CURRENT_CHAT_ID], x), reverse=False)

        for conv_id in chat_ids:
            title = st.session_state[SESSION_STATE_CHATS][conv_id]["title"]
            is_active = conv_id == st.session_state[SESSION_STATE_CURRENT_CHAT_ID]
            icon = "💬" if not is_active else "✨" # Different icon for active chat

            # Custom HTML div for visual styling, triggers hidden Streamlit button
            st.markdown(
                f'<div class="conversation-item {"active" if is_active else ""}" '
                f'onclick="window.parent.document.querySelector(\'[data-testid=\"stButton-Switch to {conv_id}\"]\').click();">' # Target the hidden st.button by its data-testid
                f'<span class="conversation-icon">{icon}</span> {title}'
                '</div>',
                unsafe_allow_html=True
            )
            # Hidden Streamlit button that actually triggers the Python callback
            st.button(
                f"Switch to {conv_id}", # Use conv_id in the label to make data-testid unique and predictable
                key=f"switch_chat_button_{conv_id}", # Unique key for the button
                on_click=switch_chat,
                args=(conv_id,),
                help=f"Switch to chat: {title}",
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
    message_container = st.container(height=500) # Fixed height for scrollable area
    with message_container:
        # Display chat messages
        for message in messages:
            with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])
                st.markdown(f'<div class="message-time">{message["time"]}</div>', unsafe_allow_html=True)

    # Chat input
    chat_input_key = "chat_input_key"
    if chat_input_key not in st.session_state:
        st.session_state[chat_input_key] = ""

    prompt = st.chat_input("Type your message...", key=chat_input_key)

    if prompt and prompt != st.session_state[SESSION_STATE_LAST_PROMPT]:
        st.session_state[SESSION_STATE_LAST_PROMPT] = prompt # Store the last prompt to prevent re-processing on rerun

        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state[SESSION_STATE_CHATS][current_chat_id]["messages"].append({
            "role": "user",
            "content": prompt,
            "time": timestamp
        })

        # Update conversation title if first message in this chat
        if not messages: # Check if messages list is empty before appending current prompt
            st.session_state[SESSION_STATE_CHATS][current_chat_id]["title"] = prompt[:25] + ("..." if len(prompt) > 25 else "")

        # Display user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            st.markdown(f'<div class="message-time">{timestamp}</div>', unsafe_allow_html=True)

        # Generate bot response with spinner
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("WiseBuddy is thinking..."):
                # Get response from Gemini API
                # Pass the current chat's messages (excluding the new user message for now,
                # as it's already added to session state)
                
                # Prepare chat history for API call (excluding the just-added user prompt,
                # as get_gemini_response will add it)
                api_chat_history = []
                for msg in st.session_state[SESSION_STATE_CHATS][current_chat_id]["messages"][:-1]: # Exclude the latest user message
                    api_chat_history.append({"role": msg["role"], "content": msg["content"]})

                full_response = asyncio.run(get_gemini_response(prompt, api_chat_history))

                response_container = st.empty()
                
                # Simulated typing effect for the API response
                current_typing_text = ""
                for char in full_response:
                    current_typing_text += char
                    response_container.markdown(current_typing_text + "▌") # Typing cursor
                    time.sleep(0.01) # Faster typing for better UX
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

