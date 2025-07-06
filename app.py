import streamlit as st
import time
import uuid
from typing import List, Dict, Optional, Callable

# ================ CONSTANTS & CONFIGURATION ================
PRIMARY_COLOR = "#5a7d9a"
ACCENT_COLOR = "#8cabc2"
BACKGROUND_COLOR = "#f0f2f5"
CHAT_BOT_BG_COLOR = "#ffffff"
SIDEBAR_BG_COLOR = "#3f5e82"
USER_MESSAGE_COLOR = "#a3c2e0"
BOT_MESSAGE_COLOR = "#e0e7ee"
TEXT_COLOR_DARK = "#333"
TEXT_COLOR_LIGHT = "#ffffff"
BORDER_COLOR_LIGHT = "#e0e0e0"

# Configure Streamlit page
st.set_page_config(
    page_title="WiseBuddy Chatbot",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ================ SESSION STATE MANAGEMENT ================
class SessionStateManager:
    """Manages initialization and access to session state variables"""
    
    @staticmethod
    def initialize():
        """Initialize all session state variables."""
        defaults = {
            "chat_history": SessionStateManager._get_default_chat_history(),
            "current_chat_id": None,
            "action_target_chat_id": None, # ID of the chat currently being acted upon (rename/delete)
            "action_type": None,          # 'rename' or 'delete'
            "show_chat_actions_for_id": None, # ID of the chat whose rename/delete buttons are visible
            "show_modal": False,
            "modal_title": "",
            "modal_message": "",
            "modal_confirm_callback": None,
            "typing_indicator_placeholder": None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
        # Set current chat if not set and history exists
        if st.session_state.current_chat_id is None and st.session_state.chat_history:
            st.session_state.current_chat_id = st.session_state.chat_history[0]['id']

    @staticmethod
    def _get_default_chat_history() -> List[Dict]:
        """Return default chat history structure."""
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
            {'id': str(uuid. 風), 'title': 'Coding Debugging Session', 'icon': 'code', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Financial Planning Tips', 'icon': 'chart-line', 'messages': []},
            {'id': str(uuid.uuid4()), 'title': 'Book Recommendations', 'icon': 'book', 'messages': []},
        ]

# ================ CHAT MANAGEMENT FUNCTIONS ================
class ChatManager:
    """Handles chat-related operations and data management."""
    
    @staticmethod
    def get_current_chat() -> Optional[Dict]:
        """Retrieves the currently active chat dictionary."""
        for chat in st.session_state.chat_history:
            if chat['id'] == st.session_state.current_chat_id:
                return chat
        return None

    @staticmethod
    def get_current_messages() -> List[Dict]:
        """Retrieves the list of messages for the current chat."""
        current_chat = ChatManager.get_current_chat()
        return current_chat['messages'] if current_chat else []

    @staticmethod
    def add_message(role: str, content: str):
        """Adds a new message to the current chat's message list."""
        current_chat = ChatManager.get_current_chat()
        if current_chat:
            current_chat['messages'].append({"role": role, "content": content})

    @staticmethod
    def create_new_chat():
        """Creates a new chat session and sets it as the current chat."""
        new_chat = {
            'id': str(uuid.uuid4()),
            'title': 'New Chat',
            'icon': 'comment', # Default icon for new chats
            'messages': [
                {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"}
            ]
        }
        st.session_state.chat_history.insert(0, new_chat) # Add to the beginning
        ChatManager.set_current_chat(new_chat['id']) # Set as current
        st.rerun() # Rerun to update UI

    @staticmethod
    def set_current_chat(chat_id: str):
        """Sets the active chat by ID and clears any pending actions."""
        st.session_state.current_chat_id = chat_id
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.session_state.show_chat_actions_for_id = None # Hide action buttons
        st.rerun() # Rerun to update UI

    @staticmethod
    def rename_chat(chat_id: str, new_title: str):
        """Renames a specific chat session."""
        if not new_title.strip():
            ChatManager.add_message("assistant", "Chat title cannot be empty.")
            st.session_state.action_target_chat_id = None # Clear action
            st.session_state.action_type = None
            st.session_state.show_chat_actions_for_id = None
            st.rerun()
            return
            
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                if new_title != chat['title']:
                    chat['title'] = new_title
                    ChatManager.add_message("assistant", f"Chat renamed to: **{new_title}**")
                break
                
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.session_state.show_chat_actions_for_id = None # Hide action buttons
        st.rerun() # Rerun to update UI

    @staticmethod
    def delete_chat(chat_id: str):
        """Deletes a specific chat session."""
        original_title = ""
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                original_title = chat['title']
                break
                
        st.session_state.chat_history = [
            chat for chat in st.session_state.chat_history 
            if chat['id'] != chat_id
        ]
        
        # If the deleted chat was the current one, switch to the first available chat
        if st.session_state.current_chat_id == chat_id:
            st.session_state.current_chat_id = (
                st.session_state.chat_history[0]['id'] 
                if st.session_state.chat_history 
                else None
            )
            
        # Notify user (only if there's still a chat to display the message in)
        if st.session_state.current_chat_id:
            ChatManager.add_message("assistant", f"Chat '{original_title}' has been deleted.")
            
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.session_state.show_chat_actions_for_id = None # Hide action buttons
        st.rerun() # Rerun to update UI

# ================ MODAL MANAGEMENT ================
class ModalManager:
    """Handles confirmation modal display and interactions."""
    
    @staticmethod
    def show(title: str, message: str, confirm_callback: Callable):
        """Displays a custom confirmation modal."""
        st.session_state.modal_title = title
        st.session_state.modal_message = message
        st.session_state.modal_confirm_callback = confirm_callback
        st.session_state.show_modal = True
        # No rerun here, modal will be rendered on the next app run

    @staticmethod
    def hide():
        """Hides the custom confirmation modal."""
        st.session_state.show_modal = False
        st.session_state.modal_title = ""
        st.session_state.modal_message = ""
        st.session_state.modal_confirm_callback = None
        # No rerun here, modal will be hidden on the next app run

    @staticmethod
    def render():
        """Renders the modal if it's active."""
        if not st.session_state.show_modal:
            return
            
        # Inject HTML for the modal
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

        # Inject JavaScript to handle button clicks and communicate back to Streamlit
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
            if st.session_state.modal_confirm_callback:
                st.session_state.modal_confirm_callback()
            ModalManager.hide()
            st.session_state.modal_confirm_clicked = False # Reset flag
            st.rerun()
        elif st.session_state.get("modal_cancel_clicked", False):
            ModalManager.hide()
            st.session_state.modal_cancel_clicked = False # Reset flag
            st.rerun()

# ================ UI COMPONENTS ================
class UICustomizer:
    """Manages custom CSS and UI styling for the entire application."""
    
    @staticmethod
    def inject_custom_css():
        """Injects custom CSS styles into the Streamlit application."""
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
            /* This targets the hidden button used to trigger chat loading */
            .stButton > button[kind="secondary"] {{
                width: 100%;
                text-align: left;
                background: none !important;
                border: none !important;
                color: inherit !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
                height: 100%; /* Make button cover the entire item area */
                position: absolute;
                top: 0;
                left: 0;
            }}
            .stButton > button[kind="secondary"]:hover {{
                background: none !important;
                color: inherit !important;
            }}

            /* Styling for the new action buttons (ellipsis, rename, delete) */
            .chat-options-btn {{
                background: none !important;
                border: none !important;
                color: {TEXT_COLOR_LIGHT} !important;
                font-size: 1.1em !important;
                padding: 5px !important;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s ease;
                margin-left: auto; /* Push to the right */
            }}
            .chat-options-btn:hover {{
                opacity: 1;
            }}

            .chat-action-buttons {{
                display: flex;
                flex-direction: column;
                gap: 5px;
                padding-left: 30px; /* Indent actions slightly */
                margin-top: 5px;
                margin-bottom: 10px;
            }}
            .chat-action-buttons .stButton > button {{
                background-color: rgba(255, 255, 255, 0.1) !important;
                color: {TEXT_COLOR_LIGHT} !important;
                border-radius: 5px !important;
                padding: 5px 10px !important;
                font-size: 0.85em !important;
                text-align: center;
                box-shadow: none !important;
            }}
            .chat-action-buttons .stButton > button:hover {{
                background-color: rgba(255, 255, 255, 0.2) !important;
            }}

            .rename-input-container {{
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-top: 10px;
                margin-bottom: 15px;
            }}
            .rename-input-container .stTextInput > div > div > input {{
                background-color: rgba(255, 255, 255, 0.2) !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                color: {TEXT_COLOR_LIGHT} !important;
                border-radius: 5px !important;
                padding: 8px !important;
            }}
            .rename-input-container .stTextInput > label {{
                color: {TEXT_COLOR_LIGHT} !important;
                font-size: 0.9em;
            }}
            .rename-input-container .stButton > button {{
                background-color: {PRIMARY_COLOR} !important;
                color: {TEXT_COLOR_LIGHT} !important;
                border-radius: 5px !important;
                padding: 8px 15px !important;
                font-size: 0.9em !important;
                box-shadow: none !important;
            }}
            .rename-input-container .stButton > button:hover {{
                background-color: #4a6c8a !important;
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
    """Renders the sidebar UI components and manages their interactions."""
    
    @staticmethod
    def render():
        """Renders the sidebar including header, new chat button, and chat list."""
        with st.sidebar:
            st.markdown('<div class="sidebar-header"><span>Chats</span></div>', unsafe_allow_html=True)
            st.button("➕ New Chat", on_click=ChatManager.create_new_chat, use_container_width=True, key="new_chat_button")
            st.markdown('<ul class="sidebar-history-list">', unsafe_allow_html=True)
            
            for chat in st.session_state.chat_history:
                SidebarRenderer._render_chat_item(chat)
                
            st.markdown('</ul>', unsafe_allow_html=True)
            # Render rename input or delete modal if an action is pending
            SidebarRenderer._render_action_inputs()

    @staticmethod
    def _render_chat_item(chat: Dict):
        """Renders an individual chat item in the sidebar, including its title, icon, and action button."""
        is_active = chat['id'] == st.session_state.current_chat_id
        active_class = "active" if is_active else ""
        
        # Use a container to group the chat item and its potential action buttons
        with st.container():
            # Create two columns for the chat title/icon and the options button
            col_title, col_options = st.columns([0.8, 0.2])
            
            with col_title:
                # Use markdown to render the custom-styled chat item
                st.markdown(f"""
                    <div class="sidebar-history-item {active_class}" 
                         style="margin-bottom:0 !important; border:none !important; background:none !important;">
                        <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                        <span class="chat-title">{chat['title']}</span>
                    </div>
                """, unsafe_allow_html=True)
                # This hidden button makes the main area of the chat item clickable to load the chat
                st.button(" ", key=f"load_chat_hidden_{chat['id']}", 
                         on_click=ChatManager.set_current_chat, args=(chat['id'],), 
                         use_container_width=True, type="secondary") # Use secondary type for hidden styling

            with col_options:
                # Button to toggle the visibility of rename/delete actions for this chat
                if st.button("...", key=f"toggle_actions_{chat['id']}", help="More options", 
                             type="secondary", # Use secondary type for hidden styling
                             on_click=SidebarRenderer._toggle_chat_actions_visibility, args=(chat['id'],)):
                    pass # The on_click handles the state change

            # Conditionally render the rename/delete buttons if this chat's actions are toggled
            if st.session_state.show_chat_actions_for_id == chat['id']:
                st.markdown('<div class="chat-action-buttons">', unsafe_allow_html=True)
                st.button("Rename", key=f"rename_btn_{chat['id']}", on_click=SidebarRenderer._set_action_for_rename, args=(chat['id'],))
                st.button("Delete", key=f"delete_btn_{chat['id']}", on_click=SidebarRenderer._set_action_for_delete, args=(chat['id'],))
                st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _toggle_chat_actions_visibility(chat_id: str):
        """Toggles the visibility of rename/delete buttons for a specific chat."""
        if st.session_state.show_chat_actions_for_id == chat_id:
            st.session_state.show_chat_actions_for_id = None # Hide if already open
        else:
            st.session_state.show_chat_actions_for_id = chat_id # Show for this chat
        # Also clear any pending rename/delete actions when toggling visibility
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None

    @staticmethod
    def _set_action_for_rename(chat_id: str):
        """Sets the state to initiate a rename action for a chat."""
        st.session_state.action_target_chat_id = chat_id
        st.session_state.action_type = 'rename'
        st.session_state.show_chat_actions_for_id = None # Hide action buttons after selection
        st.rerun()

    @staticmethod
    def _set_action_for_delete(chat_id: str):
        """Sets the state to initiate a delete action for a chat."""
        st.session_state.action_target_chat_id = chat_id
        st.session_state.action_type = 'delete'
        st.session_state.show_chat_actions_for_id = None # Hide action buttons after selection
        st.rerun()

    @staticmethod
    def _render_action_inputs():
        """Renders the rename input field or triggers the delete modal based on pending actions."""
        if not st.session_state.action_target_chat_id or not st.session_state.action_type:
            return
            
        target_chat = next(
            (c for c in st.session_state.chat_history 
             if c['id'] == st.session_state.action_target_chat_id), 
            None
        )
        
        if not target_chat:
            # If chat not found, reset action state
            st.session_state.action_target_chat_id = None
            st.session_state.action_type = None
            st.session_state.show_chat_actions_for_id = None
            return

        if st.session_state.action_type == 'rename':
            st.sidebar.markdown('<div class="rename-input-container">', unsafe_allow_html=True)
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
            st.sidebar.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.action_type == 'delete':
            ModalManager.show(
                "Confirm Deletion",
                f'Are you sure you want to delete "{target_chat["title"]}"? This action cannot be undone.',
                lambda: ChatManager.delete_chat(target_chat['id']) # Use a lambda to pass the chat_id
            )
            # After showing the modal, clear the action so it doesn't re-trigger on rerun
            st.session_state.action_target_chat_id = None
            st.session_state.action_type = None
            st.session_state.show_chat_actions_for_id = None


class ChatInterfaceRenderer:
    """Renders the main chat interface components."""
    
    @staticmethod
    def render():
        """Renders the main chat container, header, messages, and typing indicator."""
        st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
        ChatInterfaceRenderer._render_header()
        ChatInterfaceRenderer._render_messages()
        ChatInterfaceRenderer._render_typing_indicator()
        st.markdown('</div>', unsafe_allow_html=True) # Close chatbot-container

    @staticmethod
    def _render_header():
        """Renders the chat header with the WiseBuddy avatar and title."""
        st.markdown(f"""
        <div class="chatbot-header">
            <div class="header-left">
                <div class="avatar">WB</div>
                <h3>WiseBuddy</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def _render_messages():
        """Renders the chat messages using Streamlit's st.chat_message."""
        messages = ChatManager.get_current_messages()
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    @staticmethod
    def _render_typing_indicator():
        """Renders a placeholder for the typing indicator, which can be dynamically updated."""
        if st.session_state.typing_indicator_placeholder is None:
            st.session_state.typing_indicator_placeholder = st.empty()

class UserInputHandler:
    """Handles user input from the chat input box and generates simulated bot responses."""
    
    @staticmethod
    def handle():
        """Processes user input from the chat_input component."""
        if user_input := st.chat_input("Type your message...", key="main_chat_input"):
            UserInputHandler._process_user_input(user_input)

    @staticmethod
    def _process_user_input(user_input: str):
        """Adds user message, simulates bot typing, generates response, and updates UI."""
        ChatManager.add_message("user", user_input)
        
        # Show typing indicator
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
        bot_response = f"I received: '{user_input}'. This is a simulated response. In a real implementation, I would process your query."
        ChatManager.add_message("assistant", bot_response)
        
        # Clear typing indicator and rerun to display new message
        st.session_state.typing_indicator_placeholder.empty()
        st.rerun()

# ================ MAIN APPLICATION ================
def main():
    """Main application entry point for the WiseBuddy Streamlit chatbot."""
    SessionStateManager.initialize()
    UICustomizer.inject_custom_css()
    
    # Main app container HTML wrapper
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
    
    # Render components
    SidebarRenderer.render()
    ChatInterfaceRenderer.render()
    UserInputHandler.handle()
    
    # Close main-app-container HTML div
    st.markdown('</div>', unsafe_allow_html=True) 

    # Render the confirmation modal if needed
    ModalManager.render()
    
# ================ ENTRY POINT ================
if __name__ == "__main__":
    main()

