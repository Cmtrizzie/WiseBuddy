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
        """Initialize all session state variables"""
        defaults = {
            "chat_history": SessionStateManager._get_default_chat_history(),
            "current_chat_id": None,
            "action_target_chat_id": None,
            "action_type": None,
            "show_modal": False,
            "modal_title": "",
            "modal_message": "",
            "modal_confirm_callback": None,
            "typing_indicator_placeholder": None,
            "selected_chat_for_action": None # <--- ADDED: To highlight chat for action
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
        # Set current chat if not set
        if st.session_state.current_chat_id is None and st.session_state.chat_history:
            st.session_state.current_chat_id = st.session_state.chat_history[0]['id']

    @staticmethod
    def _get_default_chat_history() -> List[Dict]:
        """Return default chat history structure with icons from image"""
        return [
            {
                'id': str(uuid.uuid4()),
                'title': 'Conversation with John Doe',
                'icon': 'comments', # Speech bubble
                'messages': [
                    {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"},
                    {"role": "user", "content": "What's the weather like in Kasese, Uganda right now?"},
                    {"role": "assistant", "content": "The current time in Kasese, Western Region, Uganda is 10:48 PM, Friday, July 4, 2025. I don't have real-time weather data, but I can tell you it's likely nighttime there."},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Discussion about AI Ethics',
                'icon': 'robot', # Robot icon
                'messages': [
                    {"role": "assistant", "content": "Let's explore the ethical considerations of AI."},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Summary of Project X',
                'icon': 'file-alt', # Document icon
                'messages': [
                    {"role": "assistant", "content": "Here's a summary of Project X."},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Learning about Quantum Physics',
                'icon': 'cogs', # Gear icon
                'messages': [
                    {"role": "assistant", "content": "Let's delve into the fascinating world of quantum physics."},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Recipe for Vegan Lasagna',
                'icon': 'utensils', # Fork and knife icon
                'messages': [
                    {"role": "assistant", "content": "Looking for a delicious vegan lasagna recipe?"},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Travel Plans to Japan',
                'icon': 'plane-departure', # Airplane icon
                'messages': [
                    {"role": "assistant", "content": "Planning your trip to Japan? I can help!"},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Fitness Routine Advice',
                'icon': 'dumbbell', # Dumbbell icon
                'messages': [
                    {"role": "assistant", "content": "Need advice on your fitness routine?"},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Coding Debugging Session',
                'icon': 'code', # Code tags icon
                'messages': [
                    {"role": "assistant", "content": "Let's debug some code together."},
                ]
            },
        ]

# ================ CHAT MANAGEMENT FUNCTIONS ================
class ChatManager:
    """Handles chat-related operations and data management"""
    
    @staticmethod
    def get_current_chat() -> Optional[Dict]:
        """Get the current active chat"""
        for chat in st.session_state.chat_history:
            if chat['id'] == st.session_state.current_chat_id:
                return chat
        return None

    @staticmethod
    def get_current_messages() -> List[Dict]:
        """Get messages for the current chat"""
        current_chat = ChatManager.get_current_chat()
        return current_chat['messages'] if current_chat else []

    @staticmethod
    def add_message(role: str, content: str):
        """Add message to current chat"""
        current_chat = ChatManager.get_current_chat()
        if current_chat:
            current_chat['messages'].append({"role": role, "content": content})

    @staticmethod
    def create_new_chat():
        """Create a new chat session"""
        new_chat = {
            'id': str(uuid.uuid4()),
            'title': 'New Chat',
            'icon': 'comment', # Default icon for new chats
            'messages': [
                {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"}
            ]
        }
        
        # Add to beginning of history
        st.session_state.chat_history.insert(0, new_chat)
        st.session_state.current_chat_id = new_chat['id']
        st.session_state.selected_chat_for_action = new_chat['id'] # Select new chat for actions
        
        # Reset any pending actions
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None

    @staticmethod
    def set_current_chat(chat_id: str):
        """Set the active chat"""
        st.session_state.current_chat_id = chat_id
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        # selected_chat_for_action is handled by the button's on_click directly now

    @staticmethod
    def rename_chat(chat_id: str, new_title: str):
        """Rename a chat session"""
        if not new_title.strip():
            return
            
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                if new_title != chat['title']:
                    chat['title'] = new_title
                    # Not adding a message to current chat for rename, as it causes
                    # recursion issues if the chat itself is the one being renamed
                    # and currently active. It's more of a UI action.
                break
                
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.session_state.selected_chat_for_action = None # Clear selection after rename

    @staticmethod
    def delete_chat(chat_id: str):
        """Delete a chat session"""
        chat_to_delete = None
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                chat_to_delete = chat
                break
                
        if not chat_to_delete:
            return
            
        # Remove chat from history
        st.session_state.chat_history = [
            chat for chat in st.session_state.chat_history 
            if chat['id'] != chat_id
        ]
        
        # Handle current chat reassignment
        if st.session_state.current_chat_id == chat_id:
            st.session_state.current_chat_id = (
                st.session_state.chat_history[0]['id'] 
                if st.session_state.chat_history 
                else None
            )
            
        # Clear selected action state
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None
        st.session_state.selected_chat_for_action = None # Clear selection after delete

# ================ MODAL MANAGEMENT ================
class ModalManager:
    """Handles confirmation modal display and interactions"""
    
    @staticmethod
    def show(title: str, message: str, confirm_callback: Callable):
        """Show confirmation modal"""
        st.session_state.modal_title = title
        st.session_state.modal_message = message
        st.session_state.modal_confirm_callback = confirm_callback
        st.session_state.show_modal = True

    @staticmethod
    def hide():
        """Hide confirmation modal"""
        st.session_state.show_modal = False
        st.session_state.modal_title = ""
        st.session_state.modal_message = ""
        st.session_state.modal_confirm_callback = None

    @staticmethod
    def render():
        """Render the modal if active"""
        if not st.session_state.show_modal:
            return
            
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
            // Ensure this script is only run once or handled carefully if re-rendered
            // Streamlit re-runs scripts, so attaching listeners again can be an issue.
            // Using a simple postMessage system.
            const confirmBtn = document.getElementById('modal_confirm_btn');
            if (confirmBtn && !confirmBtn.dataset.listenerAttached) {{
                confirmBtn.onclick = () => {{
                    window.parent.postMessage({{type: 'confirmModal'}}, '*');
                }};
                confirmBtn.dataset.listenerAttached = 'true';
            }}

            const cancelBtn = document.getElementById('modal_cancel_btn');
            if (cancelBtn && !cancelBtn.dataset.listenerAttached) {{
                cancelBtn.onclick = () => {{
                    window.parent.postMessage({{type: 'cancelModal'}}, '*');
                }};
                cancelBtn.dataset.listenerAttached = 'true';
            }}
        </script>
        """, unsafe_allow_html=True)

# ================ UI COMPONENTS ================
class UICustomizer:
    """Handles custom CSS and UI styling"""
    
    @staticmethod
    def inject_custom_css():
        """Inject custom CSS styles"""
        st.markdown(f"""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            /* General app styling */
            body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR_DARK};
            }}

            .main-app-container {{
                display: flex;
                height: 100vh;
                width: 100%;
            }}

            /* Streamlit specific overrides */
            .stApp {{
                background-color: {BACKGROUND_COLOR};
            }}

            /* Adjust main content area to make space for custom sidebar */
            .main .block-container {{
                padding-top: 1rem;
                padding-bottom: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            /* Sidebar styling */
            .stSidebar {{
                background-color: {SIDEBAR_BG_COLOR};
                padding: 15px;
                border-right: 1px solid #ccc; /* Subtle border for separation */
                color: {TEXT_COLOR_LIGHT};
                box-shadow: 2px 0 5px rgba(0,0,0,0.2);
            }}
            
            /* Custom Sidebar Header */
            .sidebar-header-custom {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                margin-bottom: 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            .sidebar-header-custom .header-title {{
                font-size: 1.2rem;
                font-weight: bold;
                color: {TEXT_COLOR_LIGHT};
            }}
            .sidebar-header-custom .close-sidebar-btn {{
                background: none;
                border: none;
                color: {TEXT_COLOR_LIGHT};
                font-size: 1.2rem;
                cursor: pointer;
                padding: 5px;
                border-radius: 5px;
            }}
            .sidebar-header-custom .close-sidebar-btn:hover {{
                background-color: rgba(255,255,255,0.2);
            }}


            /* New Chat Button */
            #new_chat_button {{
                background-color: {ACCENT_COLOR};
                color: {TEXT_COLOR_DARK};
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.95rem;
                font-weight: bold;
                margin-bottom: 20px;
                transition: background-color 0.2s ease, transform 0.1s ease;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            #new_chat_button:hover {{
                background-color: #7aa1be; /* Slightly darker accent */
                transform: translateY(-1px);
            }}
            #new_chat_button:active {{
                transform: translateY(0);
                box-shadow: none;
            }}

            /* Sidebar History List */
            .sidebar-history-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}

            /* Individual Chat Item (NEW STYLES FOR IMAGE MATCH) */
            /* This targets the actual button element generated by st.button */
            .stButton > button {{
                border: none !important;
                background: none !important;
                padding: 0 !important; /* Remove default button padding */
                margin: 0 !important;
                width: 100% !important;
                text-align: left !important;
                /* Remove Streamlit's default button focus outline */
                outline: none !important; 
                box-shadow: none !important;
                transition: none !important; /* Disable Streamlit's default transitions */
            }}
            /* When Streamlit's internal button is focused */
            .stButton > button:focus:not(:active) {{
                box-shadow: none !important;
                outline: none !important;
            }}
            
            /* The wrapper for the content inside the button */
            .chat-item-wrapper {{
                display: flex;
                align-items: center;
                padding: 12px 15px; /* Adjust padding for visual appeal */
                margin-bottom: 8px; /* Space between items */
                border-radius: 8px; /* Slightly rounded corners */
                background-color: rgba(255, 255, 255, 0.1); /* Light background for items */
                color: {TEXT_COLOR_LIGHT};
                cursor: pointer;
                transition: background-color 0.2s ease, transform 0.1s ease, border 0.2s ease, box-shadow 0.2s ease;
                border: 1px solid transparent; /* Default transparent border */
                height: 50px; /* Fixed height for consistent look */
                box-sizing: border-box; /* Include padding and border in height */
            }}

            .chat-item-wrapper:hover {{
                background-color: rgba(255, 255, 255, 0.2); /* Hover effect */
                transform: translateY(-1px);
            }}
            .chat-item-wrapper:active {{
                 transform: translateY(0);
            }}

            .chat-item-wrapper.active {{
                background-color: {PRIMARY_COLOR}; /* Active chat background */
                border: 1px solid {ACCENT_COLOR}; /* Border for active item */
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.3); /* Subtle shadow for active */
            }}
            
            .chat-item-wrapper.selected-for-action {{
                border: 2px dashed {ACCENT_COLOR}; /* Dotted border for selected for action */
                box-shadow: 0 0 5px rgba(255,255,255,0.5);
            }}

            .chat-history-icon {{
                margin-right: 12px; /* Space between icon and text */
                font-size: 1.1rem;
                color: {ACCENT_COLOR}; /* Icon color */
            }}

            .chat-item-wrapper.active .chat-history-icon {{
                color: {TEXT_COLOR_LIGHT}; /* Icon color for active item */
            }}

            .chat-title {{
                font-size: 0.95rem;
                font-weight: 500;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                flex-grow: 1; /* Allow title to take available space */
            }}

            /* Action Panel for selected chat */
            .chat-action-panel {{
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid rgba(255,255,255,0.1);
                color: {TEXT_COLOR_LIGHT};
                font-size: 0.9rem;
            }}
            .chat-action-panel .stButton > button {{ /* Target buttons inside action panel */
                margin-top: 5px;
                background-color: {ACCENT_COLOR} !important; /* Override default Streamlit button bg */
                color: {TEXT_COLOR_DARK} !important;
                border-radius: 5px !important;
                border: none !important;
                padding: 8px 12px !important;
                font-size: 0.85rem !important;
                cursor: pointer !important;
                transition: background-color 0.2s ease !important;
                box-shadow: none !important;
                outline: none !important;
            }}
            .chat-action-panel .stButton > button:hover {{
                background-color: #7aa1be !important;
            }}
            .chat-action-panel #action_cancel_select_*.stButton>button {{
                background-color: #b05c5c !important; /* Red for 'X' cancel button */
                color: {TEXT_COLOR_LIGHT} !important;
            }}
            .chat-action-panel #action_cancel_select_*.stButton>button:hover {{
                background-color: #cc6d6d !important;
            }}
            .chat-action-panel .st-emotion-cache-16txt3u > div {{ /* Target the inner div of st.columns in action panel */
                 margin: 0 !important; /* Remove unwanted column margins */
                 padding: 0 3px !important; /* Small padding between action buttons */
            }}


            /* Rename Panel */
            .rename-panel {{
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid rgba(255,255,255,0.1);
                color: {TEXT_COLOR_LIGHT};
            }}
            .rename-panel h3 {{
                color: {TEXT_COLOR_LIGHT};
                font-size: 1rem;
                margin-bottom: 10px;
            }}
            /* Target Streamlit's text input component */
            .rename-panel .stTextInput > div > div > input {{
                background-color: rgba(255,255,255,0.9);
                color: {TEXT_COLOR_DARK};
                border: 1px solid {BORDER_COLOR_LIGHT};
                border-radius: 5px;
                padding: 8px;
                width: calc(100% - 16px);
                margin-bottom: 10px;
            }}
            .rename-panel .stButton > button {{ /* Target buttons inside rename panel */
                background-color: {ACCENT_COLOR} !important;
                color: {TEXT_COLOR_DARK} !important;
                border-radius: 5px !important;
                border: none !important;
                padding: 8px 12px !important;
                font-size: 0.85rem !important;
                cursor: pointer !important;
                transition: background-color 0.2s ease !important;
                box-shadow: none !important;
                outline: none !important;
            }}
            .rename-panel .stButton > button:hover {{
                background-color: #7aa1be !important;
            }}
            
            /* Chatbot Container */
            .chatbot-container {{
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                background-color: {CHAT_BOT_BG_COLOR};
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                margin: 20px;
                overflow: hidden;
            }}

            /* Chatbot Header */
            .chatbot-header {{
                display: flex;
                align-items: center;
                padding: 15px 20px;
                background-color: {PRIMARY_COLOR};
                color: {TEXT_COLOR_LIGHT};
                border-bottom: 1px solid {BORDER_COLOR_LIGHT};
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}

            .chatbot-header .header-left {{
                display: flex;
                align-items: center;
            }}

            .chatbot-header .avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: {ACCENT_COLOR};
                color: {TEXT_COLOR_DARK};
                display: flex;
                justify-content: center;
                align-items: center;
                font-weight: bold;
                margin-right: 10px;
                font-size: 1.1rem;
            }}

            .chatbot-header h3 {{
                margin: 0;
                font-size: 1.2rem;
            }}

            /* Chat Messages */
            .stChatMessage {{
                padding: 10px 20px;
                margin-bottom: 8px;
                border-radius: 15px;
                max-width: 80%;
                word-wrap: break-word;
                font-size: 0.95rem;
            }}
            /* Target the div inside stChatMessage that holds the actual message content */
            .stChatMessage > div[data-testid="stChatMessageContent"] {{
                padding: 10px 15px; /* Adjust padding for the message bubble */
            }}

            .stChatMessage:nth-child(odd) > div[data-testid="stChatMessageContent"] {{ /* User messages */
                background-color: {USER_MESSAGE_COLOR};
                color: {TEXT_COLOR_DARK};
                margin-left: auto;
                border-bottom-right-radius: 0;
            }}

            .stChatMessage:nth-child(even) > div[data-testid="stChatMessageContent"] {{ /* Bot messages */
                background-color: {BOT_MESSAGE_COLOR};
                color: {TEXT_COLOR_DARK};
                margin-right: auto;
                border-bottom-left-radius: 0;
            }}

            /* Chat input */
            .st-chat-input > div > div > div > textarea {{
                border-radius: 20px;
                padding: 10px 15px;
                border: 1px solid {BORDER_COLOR_LIGHT};
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}

            /* Typing indicator */
            .typing-indicator {{
                display: flex;
                align-items: center;
                margin: 10px 20px;
                height: 20px; /* Reserve space */
            }}

            .typing-indicator .dot {{
                width: 8px;
                height: 8px;
                background-color: {ACCENT_COLOR};
                border-radius: 50%;
                margin: 0 2px;
                animation: bounce 0.6s infinite alternate;
            }}

            .typing-indicator .dot:nth-child(2) {{
                animation-delay: 0.2s;
            }}

            .typing-indicator .dot:nth-child(3) {{
                animation-delay: 0.4s;
            }}

            @keyframes bounce {{
                from { transform: translateY(0); }
                to { transform: translateY(-5px); }
            }}

            /* Modal Styling */
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
                z-index: 1000;
                visibility: hidden;
                opacity: 0;
                transition: visibility 0s, opacity 0.3s ease;
            }}

            .modal-overlay.active {{
                visibility: visible;
                opacity: 1;
            }}

            .modal-content {{
                background-color: {CHAT_BOT_BG_COLOR};
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                text-align: center;
                max-width: 400px;
                width: 90%;
            }}

            .modal-content h4 {{
                color: {TEXT_COLOR_DARK};
                margin-top: 0;
                font-size: 1.4rem;
            }}

            .modal-content p {{
                color: {TEXT_COLOR_DARK};
                margin-bottom: 25px;
                font-size: 1rem;
            }}

            .modal-buttons {{
                display: flex;
                justify-content: center;
                gap: 15px;
            }}

            .modal-btn {{
                padding: 10px 25px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: bold;
                transition: background-color 0.2s ease, transform 0.1s ease;
            }}

            .modal-btn.confirm-btn {{
                background-color: #dc3545; /* Red for confirm delete */
                color: {TEXT_COLOR_LIGHT};
            }}

            .modal-btn.confirm-btn:hover {{
                background-color: #c82333;
                transform: translateY(-1px);
            }}

            .modal-btn.cancel-btn {{
                background-color: {BORDER_COLOR_LIGHT};
                color: {TEXT_COLOR_DARK};
            }}

            .modal-btn.cancel-btn:hover {{
                background-color: #c0c0c0;
                transform: translateY(-1px);
            }}
            
            /* Specific Streamlit internal elements to hide or reset */
            /* This targets the default Streamlit selectbox container */
            div[data-testid="stSelectbox"] {{
                display: none !important;
            }}
            /* This targets the default Streamlit button content padding */
            .stButton > button > div {{
                padding: 0 !important;
            }}
            /* Remove margins/padding from Streamlit columns if they interfere (common class for columns) */
            .st-emotion-cache-16txt3u, .st-emotion-cache-1mngp2, .st-emotion-cache-1c99rka {{ /* common column classes */
                padding: 0 !important;
                margin: 0 !important;
            }}

        </style>
        """, unsafe_allow_html=True)

class SidebarRenderer:
    """Renders the sidebar UI"""
    
    @staticmethod
    def render():
        """Render sidebar components"""
        with st.sidebar:
            # Header with "Chats" and "X" (close) button
            st.markdown(f"""
                <div class="sidebar-header-custom">
                    <span class="header-title">Chats</span>
                    <button class="close-sidebar-btn" onclick="document.querySelector('.stSidebar').style.display='none';">X</button>
                </div>
            """, unsafe_allow_html=True)
            # Note: The JS for 'X' button to close is a quick hack and might not work perfectly
            # or be consistent across all Streamlit versions/deployments.
            # A more robust solution involves Streamlit's internal state for sidebar visibility,
            # which isn't directly exposed for this kind of "close" button.

            # New Chat button - keep as is
            st.button("➕ New Chat", on_click=ChatManager.create_new_chat, use_container_width=True, key="new_chat_button")
            
            st.markdown('<ul class="sidebar-history-list">', unsafe_allow_html=True)
            
            for chat in st.session_state.chat_history:
                SidebarRenderer._render_chat_item(chat)
                
            st.markdown('</ul>', unsafe_allow_html=True)
            
            # This is where we'll render rename/delete options for the *currently selected* chat
            SidebarRenderer._render_selected_chat_actions()
            SidebarRenderer._handle_rename_input() # Call rename input separately

    @staticmethod
    def _render_chat_item(chat: Dict):
        """Render individual chat item in sidebar"""
        is_active = chat['id'] == st.session_state.current_chat_id
        is_selected_for_action = chat['id'] == st.session_state.selected_chat_for_action # NEW
        
        active_class = "active" if is_active else ""
        selected_class = "selected-for-action" if is_selected_for_action else "" # NEW

        # Use st.button with unsafe_allow_html for custom content
        # The key needs to be unique for each button
        button_html = f"""
            <div class="chat-item-wrapper {active_class} {selected_class}">
                <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                <span class="chat-title">{chat['title']}</span>
            </div>
        """
        
        if st.button(
            button_html,
            key=f"select_chat_{chat['id']}",
            help=f"Switch to or select '{chat['title']}'",
            use_container_width=True,
            unsafe_allow_html=True
        ):
            # Only switch current chat if it's different OR if we're selecting it for actions
            if st.session_state.current_chat_id != chat['id']:
                ChatManager.set_current_chat(chat['id'])
            
            # Always set this as the selected chat for actions on click
            st.session_state.selected_chat_for_action = chat['id']
            st.session_state.action_target_chat_id = None # Clear pending rename/delete for old selection
            st.session_state.action_type = None # Clear pending rename/delete for old selection
            st.rerun()

    @staticmethod
    def _render_selected_chat_actions():
        """Render action buttons (Rename, Delete, Clear Selection) for the currently selected chat."""
        if st.session_state.selected_chat_for_action:
            # Get the chat object for the selected ID
            chat = next(
                (c for c in st.session_state.chat_history 
                 if c['id'] == st.session_state.selected_chat_for_action), 
                None
            )
            if chat:
                # Only show action panel if not currently in rename mode
                if not (st.session_state.action_type == "rename" and st.session_state.action_target_chat_id == chat['id']):
                    st.sidebar.markdown(f'<div class="chat-action-panel">', unsafe_allow_html=True)
                    st.sidebar.markdown(f'**Actions for:** {chat["title"]}', unsafe_allow_html=True)
                    
                    # Using columns for horizontal buttons
                    col_rename, col_delete, col_cancel_action = st.sidebar.columns(3)
                    
                    with col_rename:
                        if st.button("Rename", key=f"action_rename_{chat['id']}", use_container_width=True):
                            st.session_state.action_target_chat_id = chat['id']
                            st.session_state.action_type = "rename"
                            st.rerun()
                    with col_delete:
                        if st.button("Delete", key=f"action_delete_{chat['id']}", use_container_width=True):
                            ModalManager.show(
                                "Confirm Deletion",
                                f'Are you sure you want to delete "{chat["title"]}"? This action cannot be undone.',
                                lambda: ChatManager.delete_chat(chat['id'])
                            )
                            # After showing modal, clear any pending rename action
                            st.session_state.action_target_chat_id = None 
                            st.session_state.action_type = None
                            st.rerun()
                    with col_cancel_action:
                        if st.button("X", key=f"action_cancel_select_{chat['id']}", help="Clear selection", use_container_width=True):
                            st.session_state.selected_chat_for_action = None
                            st.session_state.action_target_chat_id = None
                            st.session_state.action_type = None
                            st.rerun()

                    st.sidebar.markdown(f'</div>', unsafe_allow_html=True)

    @staticmethod
    def _handle_rename_input(): # Renamed from _handle_actions to be more specific
        """Handles the display and logic for the rename input field."""
        if not st.session_state.action_target_chat_id or st.session_state.action_type != "rename":
            return
            
        chat = next(
            (c for c in st.session_state.chat_history 
             if c['id'] == st.session_state.action_target_chat_id), 
            None
        )
        
        if not chat:
            return
            
        st.sidebar.markdown(f'<div class="rename-panel">', unsafe_allow_html=True)
        st.sidebar.subheader(f"Rename '{chat['title']}'")
        new_title = st.sidebar.text_input("New chat title:", value=chat['title'], 
                                         key=f"rename_input_{chat['id']}")
        
        col_save, col_cancel = st.sidebar.columns(2)
        with col_save:
            if st.button("Save", key=f"save_rename_{chat['id']}", use_container_width=True):
                ChatManager.rename_chat(chat['id'], new_title)
                st.session_state.selected_chat_for_action = None # Clear selection after rename
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key=f"cancel_rename_{chat['id']}", use_container_width=True):
                st.session_state.action_target_chat_id = None
                st.session_state.action_type = None
                st.session_state.selected_chat_for_action = None # Clear selection after cancel
                st.rerun()
        st.sidebar.markdown(f'</div>', unsafe_allow_html=True)

class ChatInterfaceRenderer:
    """Renders the main chat interface"""
    
    @staticmethod
    def render():
        """Render main chat components"""
        st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
        ChatInterfaceRenderer._render_header()
        ChatInterfaceRenderer._render_messages()
        ChatInterfaceRenderer._render_typing_indicator()
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _render_header():
        """Render chat header"""
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
        """Render chat messages"""
        messages = ChatManager.get_current_messages()
        # Use an empty container to hold messages to allow clearing/updating
        message_container = st.container(height=500, border=False) # Fixed height for scrollable chat area
        with message_container:
            for message in messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    @staticmethod
    def _render_typing_indicator():
        """Render typing indicator placeholder"""
        # Ensure the placeholder is created only once
        if "typing_indicator_placeholder" not in st.session_state or st.session_state.typing_indicator_placeholder is None:
             st.session_state.typing_indicator_placeholder = st.empty()
        # The typing indicator content is set dynamically by UserInputHandler._process_user_input

class UserInputHandler:
    """Handles user input and bot responses"""
    
    @staticmethod
    def handle():
        """Process user input and generate responses"""
        # Place chat input outside the main chat container for consistent positioning
        user_input = st.chat_input("Type your message...", key="main_chat_input")
        if user_input:
            UserInputHandler._process_user_input(user_input)

    @staticmethod
    def _process_user_input(user_input: str):
        """Process user input and generate bot response"""
        # Add user message
        ChatManager.add_message("user", user_input)
        
        # Show typing indicator
        if st.session_state.typing_indicator_placeholder:
            with st.session_state.typing_indicator_placeholder.container():
                st.markdown("""
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
                """, unsafe_allow_html=True)
                
        # Simulate processing
        time.sleep(1.5)
        
        # Generate bot response
        bot_response = f"I received: '{user_input}'. This is a simulated response. In a real implementation, I would process your query."
        ChatManager.add_message("assistant", bot_response)
        
        # Clear typing indicator
        if st.session_state.typing_indicator_placeholder:
            st.session_state.typing_indicator_placeholder.empty()
        st.rerun()

# ================ MAIN APPLICATION ================
def main():
    """Main application entry point"""
    # Initialize state and UI
    SessionStateManager.initialize()
    UICustomizer.inject_custom_css()
    
    # Setup main layout
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
    
    # Render components
    SidebarRenderer.render()
    ChatInterfaceRenderer.render()
    UserInputHandler.handle()
    
    # Close container and render modal
    st.markdown('</div>', unsafe_allow_html=True)
    ModalManager.render()
    
    # Handle modal interactions (using Streamlit's new `st.rerun()` trigger)
    # The `confirmModal` and `cancelModal` values are set by the JavaScript
    # in the modal's render function via Streamlit.setComponentValue.
    
    if st.session_state.get('confirmModal'):
        if st.session_state.modal_confirm_callback:
            st.session_state.modal_confirm_callback()
        ModalManager.hide()
        # Reset the trigger to avoid infinite loops on re-run
        st.session_state['confirmModal'] = False 
        st.rerun()
        
    elif st.session_state.get('cancelModal'):
        ModalManager.hide()
        # Reset the trigger
        st.session_state['cancelModal'] = False
        st.rerun()

# ================ ENTRY POINT ================
if __name__ == "__main__":
    # JavaScript message handler for modal
    # This script facilitates communication from the modal's HTML buttons back to Streamlit
    st.markdown("""
    <script>
        // Ensure this listener is only added once to avoid multiple triggers
        if (!window.streamlitModalListenerAdded) {
            window.addEventListener('message', (event) => {
                if (event.data.type === 'confirmModal') {
                    // console.log('Received confirmModal message'); // For debugging
                    Streamlit.setComponentValue({confirmModal: true});
                }
                else if (event.data.type === 'cancelModal') {
                    // console.log('Received cancelModal message'); // For debugging
                    Streamlit.setComponentValue({cancelModal: true});
                }
            });
            window.streamlitModalListenerAdded = true; // Mark listener as added
        }
    </script>
    """, unsafe_allow_html=True)
    
    main()

