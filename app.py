import streamlit as st
import time
import uuid

# --- Constants for Styling and Configuration ---
PRIMARY_COLOR = "#5a7d9a"  # A calming, wise blue
ACCENT_COLOR = "#8cabc2"   # Lighter blue for avatar
BACKGROUND_COLOR = "#f0f2f5" # Light background for the page
CHAT_BOT_BG_COLOR = "#ffffff" # White background for the chatbot window
SIDEBAR_BG_COLOR = "#3f5e82" # Darker blue for sidebar
USER_MESSAGE_COLOR = "#a3c2e0" # Slightly darker blue for user messages
BOT_MESSAGE_COLOR = "#e0e7ee" # Light blue/gray for bot messages
TEXT_COLOR_DARK = "#333"
TEXT_COLOR_LIGHT = "#ffffff"
BORDER_COLOR_LIGHT = "#e0e0e0"

LONG_PRESS_DURATION_MS = 500 # Not directly used in Streamlit, but kept for context

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="WiseBuddy Chatbot",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
# This injects our custom CSS to mimic the original HTML/CSS design.
# We use standard CSS as Tailwind classes are not directly parsed by Streamlit.
# Font Awesome is loaded via CDN for icons.
st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<style>
    /* General Body and Main Container Styling */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {BACKGROUND_COLOR};
        font-family: 'Inter', sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    /* Remove default gaps in Streamlit vertical blocks for tighter layout */
    [data-testid="stVerticalBlock"] {{
        gap: 0rem;
    }}

    /* Main App Container - Wrapper for sidebar and chat */
    .main-app-container {{
        display: flex;
        height: 90vh; /* Adjust height for desktop view */
        width: 100%;
        max-width: 900px; /* Max width for the whole app (sidebar + chat) */
        background-color: {BACKGROUND_COLOR};
        border-radius: 12px; /* Overall rounded corners */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        overflow: hidden; /* Hide overflow when sidebar is off-screen */
    }}

    /* Chatbot Container (Main Chat Interface) */
    .chatbot-container {{
        background-color: {CHAT_BOT_BG_COLOR};
        border-radius: 12px;
        flex-grow: 1; /* Takes up available space */
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }}

    /* Header Styling */
    .chatbot-header {{
        background-color: {PRIMARY_COLOR};
        color: {TEXT_COLOR_LIGHT};
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top-right-radius: 12px; /* Only top-right for main chat */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }}

    .header-left {{
        display: flex;
        align-items: center;
    }}

    .avatar {{
        width: 40px;
        height: 40px;
        background-color: {ACCENT_COLOR};
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 1.2em;
        margin-right: 10px;
        color: {TEXT_COLOR_LIGHT};
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }}

    .chatbot-header h3 {{
        margin: 0;
        font-size: 1.2em;
        font-weight: 600;
    }}

    /* Streamlit Chat Message Styling */
    [data-testid="stChatMessage"] {{
        margin-bottom: 10px !important;
    }}

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
        padding: 10px 15px !important;
        border-radius: 18px !important;
        line-height: 1.4 !important;
        word-wrap: break-word !important;
    }}

    /* User message bubble */
    [data-testid="stChatMessage"][data-user-message="true"] [data-testid="stMarkdownContainer"] {{
        background-color: {USER_MESSAGE_COLOR} !important;
        color: {TEXT_COLOR_LIGHT} !important;
        border-bottom-right-radius: 4px !important;
    }}

    /* Bot message bubble */
    [data-testid="stChatMessage"][data-user-message="false"] [data-testid="stMarkdownContainer"] {{
        background-color: {BOT_MESSAGE_COLOR} !important;
        color: {TEXT_COLOR_DARK} !important;
        border-bottom-left-radius: 4px !important;
    }}

    /* Quick Replies */
    .quick-replies {{
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }}

    .quick-reply-btn {{
        background-color: #d1e2f3;
        color: #3f5e82;
        border: 1px solid #b3d1ed;
        border-radius: 20px;
        padding: 8px 15px;
        font-size: 0.85em;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
        white-space: nowrap;
    }}

    .quick-reply-btn:hover {{
        background-color: #c0d7ee;
        transform: translateY(-1px);
    }}

    .quick-reply-btn:active {{
        transform: translateY(0);
    }}

    /* Typing Indicator Animation */
    @keyframes bounce {{
        0%, 80%, 100% {{ transform: translateY(0); }}
        40% {{ transform: translateY(-8px); }}
    }}

    .typing-indicator {{
        display: flex;
        align-items: center;
        gap: 4px;
        background-color: {BOT_MESSAGE_COLOR};
        border-bottom-left-radius: 4px;
        width: fit-content;
        padding: 10px 15px;
        margin-top: 10px;
    }}

    .typing-indicator .dot {{
        width: 8px;
        height: 8px;
        background-color: {ACCENT_COLOR};
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out;
    }}

    .typing-indicator .dot:nth-child(2) {{
        animation-delay: 0.2s;
    }}

    .typing-indicator .dot:nth-child(3) {{
        animation-delay: 0.4s;
    }}

    /* Streamlit Chat Input Styling */
    [data-testid="stChatInput"] {{
        padding: 15px 20px !important;
        background-color: #f7f9fb !important;
        border-top: 1px solid {BORDER_COLOR_LIGHT} !important;
        border-bottom-right-radius: 12px !important;
    }}
    [data-testid="stChatInput"] > div > div {{
        border-radius: 25px !important;
        border: 1px solid #dcdcdc !important;
    }}
    [data-testid="stChatInput"] > div > div:focus-within {{
        border-color: {PRIMARY_COLOR} !important;
        box-shadow: 0 0 0 3px rgba(90, 125, 154, 0.2) !important;
    }}
    [data-testid="stChatInput"] button {{
        background-color: {PRIMARY_COLOR} !important;
        color: {TEXT_COLOR_LIGHT} !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-size: 1.2em !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        transition: background-color 0.2s ease, transform 0.1s ease !important;
    }}
    [data-testid="stChatInput"] button:hover {{
        background-color: #4a6c8a !important;
        transform: translateY(-1px) !important;
    }}
    [data-testid="stChatInput"] button:active {{
        transform: translateY(0) !important;
    }}

    /* --- Sidebar Specific Styles --- */
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG_COLOR} !important;
        color: {TEXT_COLOR_LIGHT} !important;
        border-top-left-radius: 12px;
        border-bottom-left-radius: 12px;
        padding-top: 0 !important;
    }}

    [data-testid="stSidebarHeader"] {{
        background-color: {SIDEBAR_BG_COLOR} !important;
        color: {TEXT_COLOR_LIGHT} !important;
        padding: 15px 20px !important;
        font-size: 1.2em !important;
        font-weight: 600 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0 !important;
    }}

    /* Sidebar History List - Custom Styling */
    .sidebar-history-list {{
        list-style-type: none !important; /* Force remove bullets */
        padding: 10px !important;
        margin: 0 !important;
    }}

    .sidebar-history-item {{
        display: flex;
        align-items: center;
        padding: 14px 15px;
        margin-bottom: 15px; /* Increased spacing */
        cursor: pointer;
        transition: background-color 0.2s ease;
        font-size: 0.95em;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px; /* Slightly more rounded */
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: {TEXT_COLOR_LIGHT}; /* Ensure text color is white */
    }}

    .sidebar-history-item:last-child {{
        margin-bottom: 0;
    }}

    .sidebar-history-item:hover {{
        background-color: rgba(255, 255, 255, 0.15);
    }}

    .sidebar-history-item.active {{
        background-color: rgba(255, 255, 255, 0.25);
        font-weight: bold;
        border-color: rgba(255, 255, 255, 0.3);
    }}

    .chat-history-icon {{
        margin-right: 10px;
        font-size: 14px;
        opacity: 0.8;
    }}

    /* Streamlit button specific styling for sidebar items to make them look like list items */
    .stButton > button {{
        width: 100%;
        text-align: left;
        background: none !important;
        border: none !important;
        color: inherit !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }}
    .stButton > button:hover {{
        background: none !important;
        color: inherit !important;
    }}

    /* Custom Confirmation Modal */
    .modal-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999; /* Highest z-index for modal */
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.2s ease, visibility 0.2s ease;
    }}

    .modal-overlay.active {{
        opacity: 1;
        visibility: visible;
    }}

    .modal-content {{
        background-color: {CHAT_BOT_BG_COLOR};
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        max-width: 350px;
        width: 90%;
        text-align: center;
        transform: translateY(-20px);
        opacity: 0;
        transition: transform 0.2s ease, opacity 0.2s ease;
    }}

    .modal-overlay.active .modal-content {{
        transform: translateY(0);
        opacity: 1;
    }}

    .modal-content h4 {{
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 1.2em;
        color: {TEXT_COLOR_DARK};
    }}

    .modal-content p {{
        margin-bottom: 25px;
        color: #555;
        line-height: 1.5;
    }}

    .modal-buttons {{
        display: flex;
        justify-content: space-around;
        gap: 15px;
    }}

    .modal-btn {{
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
        flex: 1;
        border: none; /* Ensure no default button border */
    }}

    .modal-btn.confirm-btn {{
        background-color: #ef4444; /* Red for delete */
        color: {TEXT_COLOR_LIGHT};
    }}

    .modal-btn.confirm-btn:hover {{
        background-color: #dc2626;
        transform: translateY(-1px);
    }}

    .modal-btn.cancel-btn {{
        background-color: #e5e7eb; /* Light gray for cancel */
        color: #374151;
    }}

    .modal-btn.cancel-btn:hover {{
        background-color: #d1d5db;
        transform: translateY(-1px);
    }}

    /* Streamlit specific overrides for main content area */
    [data-testid="stSidebarContent"] {{
        padding-bottom: 0 !important;
    }}
    [data-testid="stVerticalBlock"] > div:first-child {{
        padding-top: 0 !important;
    }}
    [data-testid="stVerticalBlock"] > div:last-child {{
        padding-bottom: 0 !important;
    }}

    /* Media queries for responsiveness */
    @media (max-width: 767px) {{
        .main-app-container {{
            border-radius: 0;
            box-shadow: none;
            height: 100vh;
        }}
        .chatbot-container {{
            border-radius: 0;
        }}
        .chatbot-header {{
            border-radius: 0;
        }}
        [data-testid="stChatInput"] {{
            border-radius: 0 !important;
        }}
        [data-testid="stSidebar"] {{
            border-radius: 0 !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
def _initialize_session_state():
    """Initializes all necessary session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {'id': str(uuid.uuid4()), 'title': 'Conversation with John Doe', 'icon': 'comments', 'messages': [
                {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"},
                {"role": "user", "content": "What's the weather like in Kasese, Uganda right now?"},
                {"role": "assistant", "content": "The current time in Kasese, Western Region, Uganda is 10:48 PM, Friday, July 4, 2025. I don't have real-time weather data, but I can tell you it's likely nighttime there."},
            ]},
            {'id': str(uuid.uuid4()), 'title': 'Discussion about AI Ethics', 'icon': 'robot', 'messages': [
                {"role": "assistant", "content": "Welcome to our discussion on AI Ethics."},
                {"role": "user", "content": "What are the main concerns?"},
                {"role": "assistant", "content": "Key concerns include bias, privacy, accountability, and the impact on employment."},
            ]},
            {'id': str(uuid.uuid4()), 'title': 'Summary of Project X', 'icon': 'file-alt', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Learning about Quantum Physics', 'icon': 'atom', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Recipe for Vegan Lasagna', 'icon': 'utensils', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Travel Plans to Japan', 'icon': 'plane', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Fitness Routine Advice', 'icon': 'dumbbell', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Coding Debugging Session', 'icon': 'code', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Financial Planning Tips', 'icon': 'chart-line', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Book Recommendations', 'icon': 'book', 'messages': []},
        ]

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = st.session_state.chat_history[0]['id'] if st.session_state.chat_history else None

    # State for rename/delete actions
    if "action_target_chat_id" not in st.session_state:
        st.session_state.action_target_chat_id = None # ID of the chat being renamed/deleted
    if "action_type" not in st.session_state:
        st.session_state.action_type = None # 'rename' or 'delete'

    # State for custom modal
    if "show_modal" not in st.session_state:
        st.session_state.show_modal = False
    if "modal_title" not in st.session_state:
        st.session_state.modal_title = ""
    if "modal_message" not in st.session_state:
        st.session_state.modal_message = ""
    if "modal_confirm_callback" not in st.session_state:
        st.session_state.modal_confirm_callback = None

# --- Chat Data Management Functions ---
def _get_current_chat_messages():
    """Retrieves messages for the currently active chat."""
    for chat in st.session_state.chat_history:
        if chat['id'] == st.session_state.current_chat_id:
            return chat['messages']
    return []

def _add_message_to_current_chat(role: str, content: str):
    """Adds a new message to the current chat's message list."""
    for chat in st.session_state.chat_history:
        if chat['id'] == st.session_state.current_chat_id:
            chat['messages'].append({"role": role, "content": content})
            break

def _set_current_chat(chat_id: str):
    """Sets the active chat and reruns the app."""
    st.session_state.current_chat_id = chat_id
    st.session_state.action_target_chat_id = None # Clear any pending rename/delete actions
    st.session_state.action_type = None
    st.rerun()

def _create_new_chat():
    """Creates a new chat session and sets it as current."""
    new_chat_id = str(uuid.uuid4())
    st.session_state.chat_history.insert(0, {
        'id': new_chat_id,
        'title': 'New Chat',
        'icon': 'comment',
        'messages': [
            {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"}
        ]
    })
    _set_current_chat(new_chat_id)

def _rename_chat(chat_id: str, new_title: str):
    """Renames a chat in the history."""
    for chat in st.session_state.chat_history:
        if chat['id'] == chat_id:
            if new_title and new_title != chat['title']:
                chat['title'] = new_title
                _add_message_to_current_chat("assistant", f"Chat renamed to: **{new_title}**")
            break
    st.session_state.action_target_chat_id = None
    st.session_state.action_type = None
    st.rerun()

def _delete_chat(chat_id: str):
    """Deletes a chat from the history."""
    original_title = ""
    for chat in st.session_state.chat_history:
        if chat['id'] == chat_id:
            original_title = chat['title']
            break

    st.session_state.chat_history = [chat for chat in st.session_state.chat_history if chat['id'] != chat_id]
    
    # If the deleted chat was the current one, switch to the first available chat
    if st.session_state.current_chat_id == chat_id:
        st.session_state.current_chat_id = st.session_state.chat_history[0]['id'] if st.session_state.chat_history else None
    
    _add_message_to_current_chat("assistant", f"Chat '{original_title}' has been deleted.")
    st.session_state.action_target_chat_id = None
    st.session_state.action_type = None
    st.rerun()

# --- Custom Modal Functions ---
def _show_confirmation_modal(title: str, message: str, on_confirm_callback):
    """Displays a custom confirmation modal."""
    st.session_state.modal_title = title
    st.session_state.modal_message = message
    st.session_state.modal_confirm_callback = on_confirm_callback
    st.session_state.show_modal = True
    # No rerun here, modal will be rendered on next app run

def _hide_confirmation_modal():
    """Hides the custom confirmation modal."""
    st.session_state.show_modal = False
    st.session_state.modal_title = ""
    st.session_state.modal_message = ""
    st.session_state.modal_confirm_callback = None
    # No rerun here, modal will be hidden on next app run

def _perform_modal_confirm():
    """Executes the stored callback for the modal confirmation."""
    if st.session_state.modal_confirm_callback:
        st.session_state.modal_confirm_callback()
    _hide_confirmation_modal()

# --- UI Rendering Functions ---
def _render_sidebar():
    """Renders the sidebar with chat history and actions."""
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><span>Chats</span></div>', unsafe_allow_html=True)

        # New Chat Button
        st.button("➕ New Chat", on_click=_create_new_chat, use_container_width=True, key="new_chat_button")

        st.markdown('<ul class="sidebar-history-list">', unsafe_allow_html=True)
        for chat in st.session_state.chat_history:
            is_active = "active" if chat['id'] == st.session_state.current_chat_id else ""
            
            # Use columns to place the chat title and action buttons side-by-side
            col1, col2 = st.columns([0.8, 0.2])
            
            with col1:
                # Button to load the chat
                st.markdown(f"""
                    <div class="sidebar-history-item {is_active}" style="margin-bottom:0 !important; border:none !important; background:none !important;">
                        <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                        <span class="chat-title">{chat['title']}</span>
                    </div>
                """, unsafe_allow_html=True)
                # This button actually triggers the chat load. It's hidden but clickable.
                st.button(" ", key=f"load_chat_hidden_{chat['id']}", on_click=_set_current_chat, args=(chat['id'],), use_container_width=True)


            with col2:
                # Dropdown-like actions for rename/delete
                # Using a selectbox as a workaround for context menu
                action = st.selectbox(
                    "Actions",
                    ["", "Rename", "Delete"],
                    key=f"chat_actions_{chat['id']}",
                    label_visibility="collapsed"
                )
                if action == "Rename":
                    st.session_state.action_target_chat_id = chat['id']
                    st.session_state.action_type = 'rename'
                    st.rerun()
                elif action == "Delete":
                    st.session_state.action_target_chat_id = chat['id']
                    st.session_state.action_type = 'delete'
                    st.rerun()
        st.markdown('</ul>', unsafe_allow_html=True)

        # Handle rename/delete input fields and modals in the sidebar
        _handle_sidebar_actions()

def _handle_sidebar_actions():
    """Handles the display and logic for rename input and delete confirmation in sidebar."""
    if st.session_state.action_target_chat_id and st.session_state.action_type:
        target_chat = next((chat for chat in st.session_state.chat_history if chat['id'] == st.session_state.action_target_chat_id), None)

        if not target_chat:
            st.session_state.action_target_chat_id = None
            st.session_state.action_type = None
            return

        if st.session_state.action_type == 'rename':
            st.sidebar.subheader(f"Rename '{target_chat['title']}'")
            new_title = st.sidebar.text_input("New chat title:", value=target_chat['title'], key=f"rename_input_{target_chat['id']}")
            
            col_save, col_cancel = st.sidebar.columns(2)
            with col_save:
                if st.button("Save", key=f"save_rename_{target_chat['id']}"):
                    _rename_chat(target_chat['id'], new_title)
            with col_cancel:
                if st.button("Cancel", key=f"cancel_rename_{target_chat['id']}"):
                    st.session_state.action_target_chat_id = None
                    st.session_state.action_type = None
                    st.rerun()

        elif st.session_state.action_type == 'delete':
            _show_confirmation_modal(
                "Confirm Deletion",
                f"Are you sure you want to delete \"{target_chat['title']}\"? This action cannot be undone.",
                lambda: _delete_chat(target_chat['id']) # Use a lambda to pass the chat_id
            )
            # After showing the modal, clear the action so it doesn't re-trigger on rerun
            st.session_state.action_target_chat_id = None
            st.session_state.action_type = None


def _render_main_chat_interface():
    """Renders the main chat display area."""
    st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)

    # Chatbot Header
    st.markdown(f"""
    <div class="chatbot-header">
        <div class="header-left">
            <div class="avatar">WB</div>
            <h3>WiseBuddy</h3>
        </div>
        <div class="header-right relative">
            <!-- The original "..." menu is not directly implemented in Streamlit this way.
                 Main menu options are typically handled via sidebar or other Streamlit components. -->
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Display Messages
    current_messages = _get_current_chat_messages()
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Placeholder for typing indicator
    if "typing_indicator_placeholder" not in st.session_state:
        st.session_state.typing_indicator_placeholder = st.empty()

    st.markdown('</div>', unsafe_allow_html=True) # Close chatbot-container


def _handle_user_input():
    """Processes user input from the chat_input."""
    user_input = st.chat_input("Type your message...", key="main_chat_input")

    if user_input:
        _add_message_to_current_chat("user", user_input)

        # Simulate bot response with typing indicator
        with st.session_state.typing_indicator_placeholder.container():
            st.markdown("""
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            """, unsafe_allow_html=True)

        # Simulate AI processing time
        time.sleep(1.5)

        # Generate a dummy response
        bot_response = f"You said: '{user_input}'. I'm still learning, but I'll get back to you soon."
        _add_message_to_current_chat("assistant", bot_response)

        # Clear typing indicator and rerun to display new message
        st.session_state.typing_indicator_placeholder.empty()
        st.rerun()


def _render_confirmation_modal():
    """Renders the custom confirmation modal if active."""
    if st.session_state.show_modal:
        st.markdown(f"""
        <div class="modal-overlay active">
            <div class="modal-content">
                <h4>{st.session_state.modal_title}</h4>
                <p>{st.session_state.modal_message}</p>
                <div class="modal-buttons">
                    <button class="modal-btn cancel-btn" id="modal_cancel_btn">Cancel</button>
                    <button class="modal-btn confirm-btn" id="modal_confirm_btn">Confirm</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Streamlit's way to capture clicks on injected HTML buttons
        # This is a common workaround but requires a rerun to process.
        # For a truly non-blocking modal, a custom component is ideal.
        st.markdown("""
        <script>
            const confirmBtn = document.getElementById('modal_confirm_btn');
            const cancelBtn = document.getElementById('modal_cancel_btn');

            if (confirmBtn) {
                confirmBtn.onclick = function() {
                    window.parent.postMessage({
                        streamlit: {
                            command: 'SET_PAGE_STATE',
                            args: { modal_confirm_clicked: true, modal_cancel_clicked: false }
                        }
                    }, '*');
                };
            }
            if (cancelBtn) {
                cancelBtn.onclick = function() {
                    window.parent.postMessage({
                        streamlit: {
                            command: 'SET_PAGE_STATE',
                            args: { modal_cancel_clicked: true, modal_confirm_clicked: false }
                        }
                    }, '*');
                };
            }
        </script>
        """, unsafe_allow_html=True)

        # Check if the "hidden" signals from JS were received
        if st.session_state.get("modal_confirm_clicked", False):
            _perform_modal_confirm()
            st.session_state.modal_confirm_clicked = False # Reset flag
            st.rerun()
        elif st.session_state.get("modal_cancel_clicked", False):
            _hide_confirmation_modal()
            st.session_state.modal_cancel_clicked = False # Reset flag
            st.rerun()


# --- Main Application Flow ---
def main():
    """Main function to run the WiseBuddy Streamlit chatbot application."""
    _initialize_session_state()

    # Render the sidebar
    _render_sidebar()

    # Main app container HTML wrapper
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)

    # Render the main chat interface
    _render_main_chat_interface()

    # Handle user input (chat_input is always at the bottom)
    _handle_user_input()

    st.markdown('</div>', unsafe_allow_html=True) # Close main-app-container HTML div

    # Render the confirmation modal if needed
    _render_confirmation_modal()

if __name__ == "__main__":
    main()

