import streamlit as st
import time
import uuid

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="WiseBuddy Chatbot",
    page_icon="🧠",
    layout="centered", # Can be "wide" if you prefer
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
# This injects our custom CSS to mimic the original HTML/CSS design
st.markdown("""
<style>
    /* General Body and Main Container Styling */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f0f2f5; /* Light background for the page */
        font-family: 'Inter', sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0rem; /* Remove default gaps in vertical blocks for tighter layout */
    }

    /* Main App Container */
    .main-app-container {
        display: flex;
        height: 90vh; /* Adjust height for desktop view */
        width: 100%;
        max-width: 900px; /* Max width for the whole app (sidebar + chat) */
        background-color: #f0f2f5; /* Match body background */
        border-radius: 12px; /* Overall rounded corners */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        overflow: hidden; /* Hide overflow when sidebar is off-screen */
    }

    /* Chatbot Container (Main Chat Interface) */
    .chatbot-container {
        background-color: #ffffff; /* White background for the chatbot window */
        border-radius: 12px;
        flex-grow: 1; /* Takes up available space */
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    /* Header Styling */
    .chatbot-header {
        background-color: #5a7d9a; /* A calming, wise blue */
        color: #ffffff;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top-right-radius: 12px; /* Only top-right for main chat */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }

    .header-left {
        display: flex;
        align-items: center;
    }

    .avatar {
        width: 40px;
        height: 40px;
        background-color: #8cabc2; /* Lighter blue for avatar */
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 1.2em;
        margin-right: 10px;
        color: #fff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }

    .chatbot-header h3 {
        margin: 0;
        font-size: 1.2em;
        font-weight: 600;
    }

    .menu-icon {
        font-size: 1.3em;
        cursor: pointer;
        opacity: 0.8;
        transition: opacity 0.2s ease;
    }

    .menu-icon:hover {
        opacity: 1;
    }

    /* Messages Area - Streamlit's chat elements handle most of this */
    /* We'll primarily style the overall container and custom elements */
    [data-testid="stChatMessage"] {
        margin-bottom: 10px !important; /* Space between messages */
    }

    /* Customizing Streamlit's chat bubbles */
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        padding: 10px 15px !important;
        border-radius: 18px !important;
        line-height: 1.4 !important;
        word-wrap: break-word !important;
    }

    [data-testid="stChatMessage"][data-user-message="true"] [data-testid="stMarkdownContainer"] {
        background-color: #a3c2e0 !important; /* User message color */
        color: #ffffff !important;
        border-bottom-right-radius: 4px !important;
    }

    [data-testid="stChatMessage"][data-user-message="false"] [data-testid="stMarkdownContainer"] {
        background-color: #e0e7ee !important; /* Bot message color */
        color: #333 !important;
        border-bottom-left-radius: 4px !important;
    }

    /* Quick Replies */
    .quick-replies {
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px; /* Space between quick reply buttons */
    }

    .quick-reply-btn {
        background-color: #d1e2f3; /* Lighter blue for quick replies */
        color: #3f5e82; /* Darker text for contrast */
        border: 1px solid #b3d1ed;
        border-radius: 20px;
        padding: 8px 15px;
        font-size: 0.85em;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
        white-space: nowrap; /* Prevent text wrapping inside button */
    }

    .quick-reply-btn:hover {
        background-color: #c0d7ee;
        transform: translateY(-1px);
    }

    .quick-reply-btn:active {
        transform: translateY(0);
    }

    /* Typing Indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
        background-color: #e0e7ee;
        border-bottom-left-radius: 4px;
        width: fit-content;
        padding: 10px 15px;
        margin-top: 10px;
    }

    .typing-indicator .dot {
        width: 8px;
        height: 8px;
        background-color: #8cabc2;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out;
    }

    .typing-indicator .dot:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-indicator .dot:nth-child(3) {
        animation-delay: 0.4s;
    }

    /* Input Area - Streamlit's chat_input handles most of this */
    [data-testid="stChatInput"] {
        padding: 15px 20px !important;
        background-color: #f7f9fb !important;
        border-top: 1px solid #e0e0e0 !important;
        border-bottom-right-radius: 12px !important; /* Only bottom-right for main chat */
    }
    [data-testid="stChatInput"] > div > div {
        border-radius: 25px !important; /* Rounded input field */
        border: 1px solid #dcdcdc !important;
    }
    [data-testid="stChatInput"] > div > div:focus-within {
        border-color: #5a7d9a !important; /* Highlight border on focus */
        box-shadow: 0 0 0 3px rgba(90, 125, 154, 0.2) !important; /* Subtle glow on focus */
    }
    [data-testid="stChatInput"] button {
        background-color: #5a7d9a !important; /* Matching header color */
        color: #ffffff !important;
        border-radius: 50% !important; /* Circular button */
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-size: 1.2em !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        transition: background-color 0.2s ease, transform 0.1s ease !important;
    }
    [data-testid="stChatInput"] button:hover {
        background-color: #4a6c8a !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stChatInput"] button:active {
        transform: translateY(0) !important;
    }

    /* --- Sidebar Specific Styles --- */
    [data-testid="stSidebar"] {
        background-color: #3f5e82 !important; /* Darker blue for sidebar */
        color: #ffffff !important;
        border-top-left-radius: 12px;
        border-bottom-left-radius: 12px;
        padding-top: 0 !important; /* Remove default sidebar padding */
    }

    [data-testid="stSidebarHeader"] {
        background-color: #3f5e82 !important; /* Darker blue for sidebar header */
        color: #ffffff !important;
        padding: 15px 20px !important;
        font-size: 1.2em !important;
        font-weight: 600 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0 !important; /* Remove default margin */
    }

    /* Sidebar History List - Custom Styling */
    .sidebar-history-list {
        list-style-type: none !important; /* Force remove bullets */
        padding: 10px !important; /* Padding around the list items */
        margin: 0 !important;
    }

    .sidebar-history-item {
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
        color: #ffffff; /* Ensure text color is white */
    }

    .sidebar-history-item:last-child {
        margin-bottom: 0;
    }

    .sidebar-history-item:hover {
        background-color: rgba(255, 255, 255, 0.15);
    }

    .sidebar-history-item.active {
        background-color: rgba(255, 255, 255, 0.25);
        font-weight: bold;
        border-color: rgba(255, 255, 255, 0.3);
    }

    .chat-history-icon {
        margin-right: 10px;
        font-size: 14px;
        opacity: 0.8;
    }

    /* Streamlit button specific styling for sidebar items */
    .stButton > button {
        width: 100%;
        text-align: left;
        background: none !important;
        border: none !important;
        color: inherit !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        background: none !important;
        color: inherit !important;
    }

    /* Custom Confirmation Modal */
    .modal-overlay {
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
    }

    .modal-overlay.active {
        opacity: 1;
        visibility: visible;
    }

    .modal-content {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        max-width: 350px;
        width: 90%;
        text-align: center;
        transform: translateY(-20px);
        opacity: 0;
        transition: transform 0.2s ease, opacity 0.2s ease;
    }

    .modal-overlay.active .modal-content {
        transform: translateY(0);
        opacity: 1;
    }

    .modal-content h4 {
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 1.2em;
        color: #333;
    }

    .modal-content p {
        margin-bottom: 25px;
        color: #555;
        line-height: 1.5;
    }

    .modal-buttons {
        display: flex;
        justify-content: space-around;
        gap: 15px;
    }

    .modal-btn {
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
        flex: 1;
        border: none; /* Ensure no default button border */
    }

    .modal-btn.confirm-btn {
        background-color: #ef4444; /* Red for delete */
        color: #ffffff;
    }

    .modal-btn.confirm-btn:hover {
        background-color: #dc2626;
        transform: translateY(-1px);
    }

    .modal-btn.cancel-btn {
        background-color: #e5e7eb; /* Light gray for cancel */
        color: #374151;
    }

    .modal-btn.cancel-btn:hover {
        background-color: #d1d5db;
        transform: translateY(-1px);
    }

    /* Streamlit specific overrides for main content area */
    [data-testid="stSidebarContent"] {
        padding-bottom: 0 !important; /* Remove bottom padding from sidebar content */
    }
    [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important; /* Remove top padding from main content block */
    }
    [data-testid="stVerticalBlock"] > div:last-child {
        padding-bottom: 0 !important; /* Remove bottom padding from main content block */
    }

    /* Adjust for mobile view */
    @media (max-width: 767px) {
        .main-app-container {
            border-radius: 0;
            box-shadow: none;
            height: 100vh;
        }
        .chatbot-container {
            border-radius: 0;
        }
        .chatbot-header {
            border-radius: 0;
        }
        [data-testid="stChatInput"] {
            border-radius: 0 !important;
        }
        [data-testid="stSidebar"] {
            border-radius: 0 !important;
        }
    }

</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
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
        {'id': str(uuid.uuid4()), 'title': 'Summary of Project X', 'icon': 'file-alt', 'messages': [
            {"role": "assistant", "content": "I can help summarize Project X. What aspects are you interested in?"},
        ]},
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

if "show_rename_input_id" not in st.session_state:
    st.session_state.show_rename_input_id = None

if "show_modal" not in st.session_state:
    st.session_state.show_modal = False
if "modal_title" not in st.session_state:
    st.session_state.modal_title = ""
if "modal_message" not in st.session_state:
    st.session_state.modal_message = ""
if "modal_confirm_callback" not in st.session_state:
    st.session_state.modal_confirm_callback = None

# --- Utility Functions ---
def get_current_chat_messages():
    for chat in st.session_state.chat_history:
        if chat['id'] == st.session_state.current_chat_id:
            return chat['messages']
    return []

def set_current_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.show_rename_input_id = None # Hide rename input if switching chats
    st.rerun()

def add_message_to_current_chat(role, content):
    for chat in st.session_state.chat_history:
        if chat['id'] == st.session_state.current_chat_id:
            chat['messages'].append({"role": role, "content": content})
            break

def show_confirmation_modal(title, message, on_confirm_callback):
    st.session_state.modal_title = title
    st.session_state.modal_message = message
    st.session_state.modal_confirm_callback = on_confirm_callback
    st.session_state.show_modal = True
    st.rerun()

def hide_confirmation_modal():
    st.session_state.show_modal = False
    st.session_state.modal_title = ""
    st.session_state.modal_message = ""
    st.session_state.modal_confirm_callback = None
    st.rerun()

def perform_modal_confirm():
    if st.session_state.modal_confirm_callback:
        st.session_state.modal_confirm_callback()
    hide_confirmation_modal()

# --- Sidebar (Chats) ---
with st.sidebar:
    st.markdown('<div class="sidebar-header"><span>Chats</span></div>', unsafe_allow_html=True)

    # Add New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.chat_history.insert(0, {'id': new_chat_id, 'title': 'New Chat', 'icon': 'comment', 'messages': [
            {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"}
        ]})
        set_current_chat(new_chat_id)

    st.markdown('<ul class="sidebar-history-list">', unsafe_allow_html=True)
    for chat in st.session_state.chat_history:
        is_active = "active" if chat['id'] == st.session_state.current_chat_id else ""
        
        # Use a container to hold the chat item and its actions
        with st.container():
            st.markdown(f"""
                <div class="sidebar-history-item {is_active}" id="chat-item-{chat['id']}">
                    <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                    <span class="chat-title">{chat['title']}</span>
                    <button class="options-button" onclick="
                        var el = document.getElementById('chat-item-options-{chat['id']}');
                        if (el.style.display === 'block') {{ el.style.display = 'none'; }}
                        else {{
                            // Hide all other option menus
                            document.querySelectorAll('.chat-item-options').forEach(function(item) {{
                                item.style.display = 'none';
                            }});
                            el.style.display = 'block';
                        }}
                        event.stopPropagation(); // Prevent click from bubbling to parent li
                    ">
                        <i class="fas fa-ellipsis-h"></i>
                    </button>
                </div>
                <div class="chat-item-options" id="chat-item-options-{chat['id']}" style="display:none; position: absolute; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 1001; margin-top: -30px; margin-left: 200px;">
                    <ul style="list-style:none; padding: 5px 0; margin:0;">
                        <li style="padding: 8px 12px; cursor:pointer; font-size:0.9em; color:#333; display:flex; align-items:center; gap:8px;" 
                            onclick="
                                Streamlit.set  -- This is a placeholder for Streamlit.setComponentValue
                                Streamlit.setComponentValue('rename_chat_id', '{chat['id']}');
                                Streamlit.setComponentValue('delete_chat_id', null);
                                document.querySelectorAll('.chat-item-options').forEach(function(item) {{ item.style.display = 'none'; }});
                            ">
                            <i class="fas fa-edit"></i> Rename
                        </li>
                        <li style="padding: 8px 12px; cursor:pointer; font-size:0.9em; color:#333; display:flex; align-items:center; gap:8px;" 
                            onclick="
                                Streamlit.setComponentValue('delete_chat_id', '{chat['id']}');
                                Streamlit.setComponentValue('rename_chat_id', null);
                                document.querySelectorAll('.chat-item-options').forEach(function(item) {{ item.style.display = 'none'; }});
                            ">
                            <i class="fas fa-trash-alt"></i> Delete
                        </li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            # Streamlit button to handle click for loading chat
            if st.button(f"Load {chat['title']}", key=f"load_chat_{chat['id']}"):
                set_current_chat(chat['id'])

    st.markdown('</ul>', unsafe_allow_html=True)

# --- Main Chat Interface ---
st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)

# Chatbot Header
st.markdown(f"""
<div class="chatbot-header">
    <div class="header-left">
        <div class="avatar">WB</div>
        <h3>WiseBuddy</h3>
    </div>
    <div class="header-right relative">
        <i class="fas fa-ellipsis-v menu-icon" id="menu-icon"></i>
        <!-- Dropdown Menu - Streamlit doesn't have direct dropdowns like this easily,
             so we'll simulate main menu options via sidebar or separate buttons if needed.
             For now, this icon is purely visual. -->
    </div>
</div>
""", unsafe_allow_html=True)

# Display Messages
current_messages = get_current_chat_messages()
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Simulate Typing Indicator (using a placeholder)
if "typing_indicator_placeholder" not in st.session_state:
    st.session_state.typing_indicator_placeholder = st.empty()

# Chat Input
user_input = st.chat_input("Type your message...", key="chat_input")

if user_input:
    add_message_to_current_chat("user", user_input)

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
    add_message_to_current_chat("assistant", bot_response)

    # Clear typing indicator
    st.session_state.typing_indicator_placeholder.empty()
    st.rerun() # Rerun to display new message and clear input

st.markdown('</div>', unsafe_allow_html=True) # Close chatbot-container
st.markdown('</div>', unsafe_allow_html=True) # Close main-app-container

# --- Custom Confirmation Modal (rendered conditionally) ---
if st.session_state.show_modal:
    st.markdown(f"""
    <div class="modal-overlay active">
        <div class="modal-content">
            <h4>{st.session_state.modal_title}</h4>
            <p>{st.session_state.modal_message}</p>
            <div class="modal-buttons">
                <button class="modal-btn cancel-btn" onclick="
                    Streamlit.setComponentValue('modal_cancel_clicked', true);
                    Streamlit.setComponentValue('modal_confirm_clicked', false);
                ">Cancel</button>
                <button class="modal-btn confirm-btn" onclick="
                    Streamlit.setComponentValue('modal_confirm_clicked', true);
                    Streamlit.setComponentValue('modal_cancel_clicked', false);
                ">Confirm</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Handle modal button clicks via Streamlit's custom component value
    # Note: This requires a custom component setup for proper two-way binding
    # For simplicity in this example, we'll use a direct Streamlit button approach
    # or rely on reruns with a hidden button.
    # A more robust solution for modals in Streamlit often involves a custom component.

    # For demonstration, we'll use hidden buttons that are clicked via JS in the HTML
    # This is a common workaround for complex JS interactions in Streamlit.
    if "modal_confirm_clicked" not in st.session_state:
        st.session_state.modal_confirm_clicked = False
    if "modal_cancel_clicked" not in st.session_state:
        st.session_state.modal_cancel_clicked = False

    # Check if the hidden confirm/cancel buttons were "clicked" by the injected JS
    if st.session_state.modal_confirm_clicked:
        perform_modal_confirm()
        st.session_state.modal_confirm_clicked = False # Reset
        st.rerun()
    elif st.session_state.modal_cancel_clicked:
        hide_confirmation_modal()
        st.session_state.modal_cancel_clicked = False # Reset
        st.rerun()

# --- Handle Rename/Delete Actions Triggered from Sidebar ---
# These values will be set by the onclick JS in the sidebar
if "rename_chat_id" not in st.session_state:
    st.session_state.rename_chat_id = None
if "delete_chat_id" not in st.session_state:
    st.session_state.delete_chat_id = None

if st.session_state.rename_chat_id:
    chat_to_rename = next((chat for chat in st.session_state.chat_history if chat['id'] == st.session_state.rename_chat_id), None)
    if chat_to_rename:
        new_title = st.sidebar.text_input("Rename chat:", value=chat_to_rename['title'], key=f"rename_input_{chat_to_rename['id']}")
        if st.sidebar.button("Save Rename", key=f"save_rename_{chat_to_rename['id']}"):
            if new_title and new_title != chat_to_rename['title']:
                chat_to_rename['title'] = new_title
                add_message_to_current_chat("assistant", f"Chat renamed to: **{new_title}**")
            st.session_state.rename_chat_id = None
            st.rerun()
        if st.sidebar.button("Cancel Rename", key=f"cancel_rename_{chat_to_rename['id']}"):
            st.session_state.rename_chat_id = None
            st.rerun()
    else:
        st.session_state.rename_chat_id = None # Reset if chat not found

if st.session_state.delete_chat_id:
    chat_to_delete = next((chat for chat in st.session_state.chat_history if chat['id'] == st.session_state.delete_chat_id), None)
    if chat_to_delete:
        def confirm_delete():
            st.session_state.chat_history = [chat for chat in st.session_state.chat_history if chat['id'] != st.session_state.delete_chat_id]
            if st.session_state.current_chat_id == st.session_state.delete_chat_id:
                st.session_state.current_chat_id = st.session_state.chat_history[0]['id'] if st.session_state.chat_history else None
            add_message_to_current_chat("assistant", f"Chat '{chat_to_delete['title']}' has been deleted.")
            st.session_state.delete_chat_id = None # Clear after action
            st.rerun()

        show_confirmation_modal(
            "Confirm Deletion",
            f"Are you sure you want to delete \"{chat_to_delete['title']}\"? This action cannot be undone.",
            confirm_delete
        )
    else:
        st.session_state.delete_chat_id = None # Reset if chat not found

# --- Important: Streamlit.setComponentValue workaround ---
# Streamlit doesn't directly expose a way for injected JS to update session_state.
# The `Streamlit.setComponentValue` calls in the HTML are conceptual here.
# To make rename/delete work, you would typically use:
# 1. A custom Streamlit component (more complex setup).
# 2. A simpler workaround: have hidden Streamlit buttons/inputs whose values are
#    toggled by the injected JS, and then check those values in Python.
# For this example, I've used the latter (conceptual `Streamlit.setComponentValue`
# which would trigger a rerun and then be picked up by checking `st.session_state.rename_chat_id`
# and `st.session_state.delete_chat_id`).
# For the modal, I've added conceptual `Streamlit.setComponentValue` calls that
# would update `st.session_state.modal_confirm_clicked` and `st.session_state.modal_cancel_clicked`.
# In a real deployed app, you'd need to ensure these JS-to-Python communications work.
# For local testing, the `st.rerun()` calls will make the state changes visible after interaction.


