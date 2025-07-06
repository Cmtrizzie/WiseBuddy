import streamlit as st
import time
import uuid
from typing import List, Dict, Optional, Callable

# ================ CONSTANTS & CONFIGURATION ================
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

# Configure Streamlit page
st.set_page_config(
    page_title="WiseBuddy Chatbot",
    page_icon="🧠",
    layout="centered", # Can be "wide" if you prefer
    initial_sidebar_state="expanded"
)

# ================ SESSION STATE MANAGEMENT ================
class SessionStateManager:
    """
    Manages initialization and access to Streamlit session state variables.
    Streamlit's session state is automatically persisted across reruns,
    providing the "auto-save" functionality for the application's data.
    """
    
    @staticmethod
    def initialize():
        """
        Initializes all necessary session state variables with default values
        if they are not already set.
        """
        defaults = {
            "chat_history": SessionStateManager._get_default_chat_history(),
            "current_chat_id": None,
            "action_target_chat_id": None, # ID of the chat currently being acted upon (rename/delete)
            "action_type": None,           # 'rename' or 'delete'
            "show_modal": False,           # Controls visibility of the custom confirmation modal
            "modal_title": "",
            "modal_message": "",
            "modal_confirm_callback": None, # Callback function to execute on modal confirmation
            "typing_indicator_placeholder": None # Placeholder for dynamic typing indicator
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
        # Set current chat to the first one if not already set and history exists
        if st.session_state.current_chat_id is None and st.session_state.chat_history:
            st.session_state.current_chat_id = st.session_state.chat_history[0]['id']

    @staticmethod
    def _get_default_chat_history() -> List[Dict]:
        """
        Returns a list of default chat sessions for initial application load.
        Each chat includes an ID, title, icon (for display), and messages.
        """
        return [
            {
                'id': str(uuid.uuid4()),
                'title': 'Conversation with John Doe',
                'icon': 'comments',
                'messages': [
                    {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"},
                    {"role": "user", "content": "What's the weather like in Kasese, Uganda right now?"},
                    {"role": "assistant", "content": "The current time in Kasese, Western Region, Uganda is 10:48 PM, Friday, July 4, 2025. I don't have real-time weather data, but I can tell you it's likely nighttime there."},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Discussion about AI Ethics',
                'icon': 'robot',
                'messages': [
                    {"role": "assistant", "content": "Welcome to our discussion on AI Ethics."},
                    {"role": "user", "content": "What are the main concerns?"},
                    {"role": "assistant", "content": "Key concerns include bias, privacy, accountability, and the impact on employment."},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Summary of Project X',
                'icon': 'file-alt',
                'messages': [
                    {"role": "assistant", "content": "I can help summarize Project X. What aspects are you interested in?"},
                ]
            },
            { 'id': str(uuid.uuid4()), 'title': 'Learning about Quantum Physics', 'icon': 'atom', 'messages': [] },
            { 'id': str(uuid.uuid4()), 'title': 'Recipe for Vegan Lasagna', 'icon': 'utensils', 'messages': [] },
            { 'id': str(uuid.uuid4()), 'title': 'Travel Plans to Japan', 'icon': 'plane', 'messages': [] },
            { 'id': str(uuid.uuid4()), 'title': 'Fitness Routine Advice', 'icon': 'dumbbell', 'messages': [] },
            { 'id': str(uuid.uuid4()), 'title': 'Coding Debugging Session', 'icon': 'code', 'messages': [] },
            { 'id': str(uuid.uuid4()), 'title': 'Financial Planning Tips', 'icon': 'chart-line', 'messages': [] },
            { 'id': str(uuid.uuid4()), 'title': 'Book Recommendations', 'icon': 'book', 'messages': [] },
        ]

# ================ CHAT MANAGEMENT FUNCTIONS ================
class ChatManager:
    """
    Handles all operations related to chat sessions, including
    retrieving, adding, creating, renaming, and deleting chats.
    """
    
    @staticmethod
    def get_current_chat() -> Optional[Dict]:
        """
        Retrieves the dictionary representing the currently active chat session.
        Returns None if no chat is currently active or found.
        """
        for chat in st.session_state.chat_history:
            if chat['id'] == st.session_state.current_chat_id:
                return chat
        return None

    @staticmethod
    def get_current_messages() -> List[Dict]:
        """
        Retrieves the list of messages for the currently active chat session.
        Returns an empty list if no chat is active or found.
        """
        current_chat = ChatManager.get_current_chat()
        return current_chat['messages'] if current_chat else []

    @staticmethod
    def add_message(role: str, content: str):
        """
        Adds a new message to the current chat's message list.
        Also triggers auto-naming if it's the first user message in a new chat.
        """
        current_chat = ChatManager.get_current_chat()
        if current_chat:
            current_chat['messages'].append({"role": role, "content": content})
            
            # Auto-name chat if it's a 'New Chat' and this is the first user message
            if current_chat['title'] == 'New Chat' and role == 'user' and \
               len([m for m in current_chat['messages'] if m['role'] == 'user']) == 1:
                ChatManager._auto_name_chat(current_chat, content)

    @staticmethod
    def _auto_name_chat(chat: Dict, first_user_message: str):
        """
        Generates an automatic title for a new chat based on the first user message.
        """
        words = first_user_message.split()
        # Take the first 5 words, or fewer if the message is shorter
        new_title_words = words[:5]
        new_title = " ".join(new_title_words)
        if len(words) > 5:
            new_title += "..."
        
        # Update the chat title directly in the session state
        chat['title'] = new_title
        # No need to rerun here, the main app loop will re-render the sidebar

    @staticmethod
    def create_new_chat():
        """
        Creates a new empty chat session, sets it as the current active chat,
        and adds an initial assistant welcome message.
        """
        new_chat = {
            'id': str(uuid.uuid4()),
            'title': 'New Chat', # Temporary title, will be auto-named
            'icon': 'comment', # Default icon for new chats
            'messages': [
                {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"}
            ]
        }
        
        # Add to the beginning of the chat history list
        st.session_state.chat_history.insert(0, new_chat)
        st.session_state.current_chat_id = new_chat['id']
        
        # Clear any pending actions from previous interactions
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.rerun() # Rerun to immediately display the new chat

    @staticmethod
    def set_current_chat(chat_id: str):
        """
        Sets the specified chat session as the currently active one.
        """
        st.session_state.current_chat_id = chat_id
        # Clear any pending actions when switching chats
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.rerun() # Rerun to display the selected chat

    @staticmethod
    def rename_chat(chat_id: str, new_title: str):
        """
        Renames a specific chat session. If the new title is empty or unchanged,
        no action is taken.
        """
        if not new_title.strip(): # Do not allow empty titles
            return
            
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                if new_title != chat['title']: # Only update if title has changed
                    chat['title'] = new_title
                    ChatManager.add_message(
                        "assistant", 
                        f"Chat renamed to: **{new_title}**" # Notify in chat
                    )
                break
                
        # Clear the action state
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.rerun() # Rerun to update sidebar and clear rename input

    @staticmethod
    def delete_chat(chat_id: str):
        """
        Deletes a specific chat session from the history. If the deleted chat
        was the current active chat, the active chat is switched to the first
        available chat, or set to None if no chats remain.
        """
        chat_to_delete = None
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                chat_to_delete = chat
                break
                
        if not chat_to_delete: # Chat not found, do nothing
            return
            
        # Filter out the chat to be deleted from the history
        st.session_state.chat_history = [
            chat for chat in st.session_state.chat_history 
            if chat['id'] != chat_id
        ]
        
        # If the deleted chat was the current one, reassign current_chat_id
        if st.session_state.current_chat_id == chat_id:
            st.session_state.current_chat_id = (
                st.session_state.chat_history[0]['id'] 
                if st.session_state.chat_history # If there are still chats, pick the first
                else None # Otherwise, no chat is active
            )
            
        # Add a notification message to the newly active chat (if any)
        if st.session_state.current_chat_id:
            ChatManager.add_message(
                "assistant", 
                f"Chat '{chat_to_delete['title']}' has been deleted."
            )
        
        # Clear the action state
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.rerun() # Rerun to update sidebar and main chat display

# ================ MODAL MANAGEMENT ================
class ModalManager:
    """
    Handles the display and interactions of a custom confirmation modal.
    Uses Streamlit's `st.markdown` to inject HTML/JS for the modal,
    and `window.parent.postMessage` to communicate user actions back to Streamlit.
    """
    
    @staticmethod
    def show(title: str, message: str, confirm_callback: Callable):
        """
        Sets the state to display the confirmation modal with specified title,
        message, and a callback function to execute upon confirmation.
        """
        st.session_state.modal_title = title
        st.session_state.modal_message = message
        st.session_state.modal_confirm_callback = confirm_callback
        st.session_state.show_modal = True
        # No rerun here; the modal will be rendered on the next app rerun.

    @staticmethod
    def hide():
        """
        Hides the confirmation modal and clears its associated state.
        """
        st.session_state.show_modal = False
        st.session_state.modal_title = ""
        st.session_state.modal_message = ""
        st.session_state.modal_confirm_callback = None
        # No rerun here; the modal will be hidden on the next app rerun.

    @staticmethod
    def render():
        """
        Renders the custom confirmation modal if its display state is active.
        Includes embedded JavaScript to send messages back to Streamlit.
        """
        if not st.session_state.show_modal:
            return
            
        # Inject modal HTML and JS
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
        <script>
            // Add event listeners to the modal buttons to send messages to Streamlit
            const confirmBtn = document.getElementById('modal_confirm_btn');
            const cancelBtn = document.getElementById('modal_cancel_btn');

            if (confirmBtn) {{
                confirmBtn.onclick = function() {{
                    window.parent.postMessage({{
                        streamlit: {{
                            command: 'SET_PAGE_STATE',
                            args: {{ modal_confirm_clicked: true, modal_cancel_clicked: false }}
                        }}
                    }}, '*');
                }};
            }}
            if (cancelBtn) {{
                cancelBtn.onclick = function() {{
                    window.parent.postMessage({{
                        streamlit: {{
                            command: 'SET_PAGE_STATE',
                            args: {{ modal_cancel_clicked: true, modal_confirm_clicked: false }}
                        }}
                    }}, '*');
                }};
            }}
        </script>
        """, unsafe_allow_html=True)

        # Process the messages sent from the modal's JavaScript
        # These flags are set by the JS and then read by Streamlit on rerun
        if st.session_state.get("modal_confirm_clicked", False):
            if st.session_state.modal_confirm_callback:
                st.session_state.modal_confirm_callback()
            ModalManager.hide()
            st.session_state.modal_confirm_clicked = False # Reset flag
            st.rerun() # Rerun to update state and hide modal
        elif st.session_state.get("modal_cancel_clicked", False):
            ModalManager.hide()
            st.session_state.modal_cancel_clicked = False # Reset flag
            st.rerun() # Rerun to update state and hide modal

# ================ UI CUSTOMIZATION & RENDERING ================
class UICustomizer:
    """
    Manages the injection of custom CSS styles into the Streamlit application
    to achieve the desired visual design.
    """
    
    @staticmethod
    def inject_custom_css():
        """
        Injects custom CSS styles into the Streamlit app.
        This includes general body styles, chat message styling, sidebar styling,
        and modal styling. Font Awesome is loaded for icons.
        """
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
                /* Note: Padding and margin-bottom moved to the outer Streamlit container/column */
                cursor: pointer;
                transition: background-color 0.2s ease;
                font-size: 0.95em;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px; /* Slightly more rounded */
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {TEXT_COLOR_LIGHT}; /* Ensure text color is white */
                width: 100%; /* Ensure it takes full width of its column */
                box-sizing: border-box; /* Include padding and border in element's total width and height */
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

            .chat-title {{
                flex-grow: 1;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}

            /* Streamlit button specific styling for sidebar items to make them look like list items */
            /* This targets the 'Load Chat' button that makes the whole area clickable */
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

            /* Styles for the selectbox used as actions menu */
            [data-testid="stSelectbox"] > div[data-baseweb="select"] {{
                background-color: rgba(255, 255, 255, 0.1) !important;
                border-radius: 5px !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                color: {TEXT_COLOR_LIGHT} !important;
                height: 35px; /* Adjust height to be less intrusive */
            }}
            [data-testid="stSelectbox"] > div[data-baseweb="select"] > div:first-child {{
                color: {TEXT_COLOR_LIGHT} !important; /* Text color inside selectbox */
            }}
            [data-testid="stSelectbox"] > div[data-baseweb="select"] svg {{
                color: {TEXT_COLOR_LIGHT} !important; /* Arrow icon color */
            }}
            /* Options list when selectbox is open */
            [data-baseweb="popover"] ul {{
                background-color: {SIDEBAR_BG_COLOR} !important;
                color: {TEXT_COLOR_LIGHT} !important;
            }}
            [data-baseweb="popover"] li {{
                color: {TEXT_COLOR_LIGHT} !important;
            }}
            [data-baseweb="popover"] li:hover {{
                background-color: rgba(255, 255, 255, 0.15) !important;
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

class SidebarRenderer:
    """
    Renders the sidebar UI, including the "New Chat" button,
    the list of chat sessions, and the rename/delete action interface.
    """
    
    @staticmethod
    def render():
        """
        Renders all components within the Streamlit sidebar.
        """
        with st.sidebar:
            st.markdown('<div class="sidebar-header"><span>Chats</span></div>', unsafe_allow_html=True)

            # "New Chat" button is always visible at the top of the chat list
            st.button("➕ New Chat", on_click=ChatManager.create_new_chat, use_container_width=True, key="new_chat_button")

            st.markdown('<ul class="sidebar-history-list">', unsafe_allow_html=True)
            
            # Iterate through chat history and render each item
            for chat in st.session_state.chat_history:
                SidebarRenderer._render_chat_item(chat)
                
            st.markdown('</ul>', unsafe_allow_html=True)

            # Handle rename/delete input fields and modals in the sidebar
            SidebarRenderer._handle_actions_ui()

    @staticmethod
    def _render_chat_item(chat: Dict):
        """
        Renders an individual chat item in the sidebar, including its title,
        icon, and action (Rename/Delete) selectbox.
        """
        is_active = chat['id'] == st.session_state.current_chat_id
        active_class = "active" if is_active else ""
        
        # Use Streamlit columns to align the chat title/icon and the action selectbox
        col1, col2 = st.columns([0.8, 0.2])
        
        with col1:
            # The chat item itself is rendered as markdown with custom CSS classes
            # The `st.button` below it makes the entire area clickable for loading the chat.
            st.markdown(f"""
                <div class="sidebar-history-item {active_class}" 
                     style="margin-bottom:0 !important; border:none !important; background:none !important;">
                    <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                    <span class="chat-title">{chat['title']}</span>
                </div>
            """, unsafe_allow_html=True)
            # This hidden button makes the entire area clickable to load the chat
            st.button(" ", key=f"load_chat_hidden_{chat['id']}", 
                     on_click=ChatManager.set_current_chat, args=(chat['id'],), 
                     use_container_width=True)


        with col2:
            # A selectbox is used to simulate the context menu for rename/delete actions.
            # `label_visibility="collapsed"` hides the label for a cleaner look.
            action = st.selectbox(
                "Actions", ["", "Rename", "Delete"],
                key=f"chat_actions_{chat['id']}",
                label_visibility="collapsed"
            )
            if action: # If an action is selected (not the empty string)
                SidebarRenderer._trigger_chat_action(chat, action)

    @staticmethod
    def _trigger_chat_action(chat: Dict, action: str):
        """
        Sets the session state to indicate which chat is being acted upon
        and what type of action is requested. Triggers a rerun.
        """
        st.session_state.action_target_chat_id = chat['id']
        st.session_state.action_type = action.lower()
        st.rerun() # Rerun to display the rename input or modal

    @staticmethod
    def _handle_actions_ui():
        """
        Displays the appropriate UI (rename input or confirmation modal)
        based on the `action_type` and `action_target_chat_id` in session state.
        """
        if not st.session_state.action_target_chat_id or not st.session_state.action_type:
            return # No action pending

        target_chat = next(
            (c for c in st.session_state.chat_history 
             if c['id'] == st.session_state.action_target_chat_id), 
            None
        )
        
        if not target_chat: # If the target chat no longer exists (e.g., deleted)
            st.session_state.action_target_chat_id = None
            st.session_state.action_type = None
            return

        if st.session_state.action_type == 'rename':
            st.sidebar.subheader(f"Rename '{target_chat['title']}'")
            new_title = st.sidebar.text_input("New chat title:", value=target_chat['title'], 
                                             key=f"rename_input_{target_chat['id']}")
            
            col_save, col_cancel = st.sidebar.columns(2)
            with col_save:
                if st.button("Save", key=f"save_rename_{target_chat['id']}"):
                    ChatManager.rename_chat(target_chat['id'], new_title)
            with col_cancel:
                if st.button("Cancel", key=f"cancel_rename_{target_chat['id']}"):
                    st.session_state.action_target_chat_id = None
                    st.session_state.action_type = None
                    st.rerun()

        elif st.session_state.action_type == 'delete':
            # Show confirmation modal for delete action
            ModalManager.show(
                "Confirm Deletion",
                f'Are you sure you want to delete "{target_chat["title"]}"? This action cannot be undone.',
                lambda: ChatManager.delete_chat(target_chat['id']) # Pass the delete function as callback
            )
            # After showing the modal, clear the action so it doesn't re-trigger on rerun
            # The modal's own logic will handle the rerun after confirm/cancel
            st.session_state.action_target_chat_id = None
            st.session_state.action_type = None

class ChatInterfaceRenderer:
    """
    Renders the main chat display area, including the chatbot header,
    messages, and the typing indicator.
    """
    
    @staticmethod
    def render():
        """
        Renders the main chat container and its internal components.
        """
        st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
        ChatInterfaceRenderer._render_header()
        ChatInterfaceRenderer._render_messages()
        ChatInterfaceRenderer._render_typing_indicator_placeholder()
        st.markdown('</div>', unsafe_allow_html=True) # Close chatbot-container HTML div

    @staticmethod
    def _render_header():
        """
        Renders the fixed header for the chatbot interface.
        """
        st.markdown(f"""
        <div class="chatbot-header">
            <div class="header-left">
                <div class="avatar">WB</div>
                <h3>WiseBuddy</h3>
            </div>
            <div class="header-right relative">
                <!-- Placeholder for potential future menu, not functional in Streamlit this way -->
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def _render_messages():
        """
        Renders all messages for the currently active chat using Streamlit's
        native `st.chat_message` component.
        """
        messages = ChatManager.get_current_messages()
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    @staticmethod
    def _render_typing_indicator_placeholder():
        """
        Initializes or retrieves the placeholder for the dynamic typing indicator.
        This allows the indicator to be shown/hidden dynamically without rerunning the entire app.
        """
        if st.session_state.typing_indicator_placeholder is None:
            st.session_state.typing_indicator_placeholder = st.empty()

class UserInputHandler:
    """
    Handles user input from the chat input field and simulates bot responses.
    Also manages the auto-naming feature for new chats.
    """
    
    @staticmethod
    def handle():
        """
        Processes user input from the `st.chat_input` component.
        If input is provided, it adds the user message, simulates a bot response
        with a typing indicator, and then reruns the app to update the display.
        """
        # st.chat_input is always placed at the bottom of the main content area
        if user_input := st.chat_input("Type your message...", key="main_chat_input"):
            UserInputHandler._process_user_input(user_input)

    @staticmethod
    def _process_user_input(user_input: str):
        """
        Adds the user's message, displays a typing indicator, simulates
        a bot response, and then clears the indicator.
        """
        # Add user message to the current chat history
        ChatManager.add_message("user", user_input)
        
        # Show typing indicator using the pre-defined placeholder
        with st.session_state.typing_indicator_placeholder.container():
            st.markdown("""
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            """, unsafe_allow_html=True)
            
        # Simulate AI processing time
        time.sleep(1.5) # Blocking call, but for simulation it's fine
        
        # Generate a dummy bot response
        bot_response = f"I received: '{user_input}'. This is a simulated response. In a real implementation, I would process your query using an LLM."
        ChatManager.add_message("assistant", bot_response)
        
        # Clear the typing indicator after the response
        st.session_state.typing_indicator_placeholder.empty()
        st.rerun() # Rerun the app to display the new messages and clear the input field

# ================ MAIN APPLICATION ENTRY POINT ================
def main():
    """
    The main function that orchestrates the Streamlit application.
    It initializes the session state, injects CSS, renders the UI components,
    and handles user interactions.
    """
    # Initialize all session state variables
    SessionStateManager.initialize()
    
    # Inject custom CSS for styling the application
    UICustomizer.inject_custom_css()
    
    # Render the main application container (HTML wrapper for layout)
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
    
    # Render the sidebar with chat list and actions
    SidebarRenderer.render()
    
    # Render the main chat interface (header, messages, typing indicator placeholder)
    ChatInterfaceRenderer.render()
    
    # Handle user input from the chat input field
    UserInputHandler.handle()
    
    # Close the main application container HTML div
    st.markdown('</div>', unsafe_allow_html=True) 
    
    # Render the confirmation modal if it's active
    ModalManager.render()

# ================ APPLICATION STARTUP ================
if __name__ == "__main__":
    # This JavaScript snippet is crucial for the custom modal to communicate
    # back to Streamlit when its buttons are clicked. It uses `postMessage`
    # to update Streamlit's internal state, which triggers a rerun.
    st.markdown("""
    <script>
        window.addEventListener('message', (event) => {
            if (event.data.type === 'confirmModal') {
                // Use Streamlit.setComponentValue to update a session state variable
                // This will trigger a rerun in the Streamlit app
                window.parent.postMessage({
                    streamlit: {
                        command: 'SET_PAGE_STATE',
                        args: { confirmModal: true }
                    }
                }, '*');
            }
            else if (event.data.type === 'cancelModal') {
                window.parent.postMessage({
                    streamlit: {
                        command: 'SET_PAGE_STATE',
                        args: { cancelModal: true }
                    }
                }, '*');
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Run the main application function
    main()

