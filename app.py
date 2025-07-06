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
            "typing_indicator_placeholder": None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
        # Set current chat if not set
        if st.session_state.current_chat_id is None and st.session_state.chat_history:
            st.session_state.current_chat_id = st.session_state.chat_history[0]['id']

    @staticmethod
    def _get_default_chat_history() -> List[Dict]:
        """Return default chat history structure"""
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
            # Additional sample chats would be listed here...
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
            'icon': 'comment',
            'messages': [
                {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help you today?"}
            ]
        }
        
        # Add to beginning of history
        st.session_state.chat_history.insert(0, new_chat)
        st.session_state.current_chat_id = new_chat['id']
        
        # Reset any pending actions
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None

    @staticmethod
    def set_current_chat(chat_id: str):
        """Set the active chat"""
        st.session_state.current_chat_id = chat_id
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None

    @staticmethod
    def rename_chat(chat_id: str, new_title: str):
        """Rename a chat session"""
        if not new_title.strip():
            return
            
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                if new_title != chat['title']:
                    chat['title'] = new_title
                    ChatManager.add_message(
                        "assistant", 
                        f"Chat renamed to: **{new_title}**"
                    )
                break
                
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None

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
            
        # Notify user
        if st.session_state.current_chat_id:
            ChatManager.add_message(
                "assistant", 
                f"Chat '{chat_to_delete['title']}' has been deleted."
            )
            
        st.session_state.action_target_chat_id = None
        st.session_state.action_type = None

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
            document.getElementById('modal_confirm_btn').onclick = () => {{
                window.parent.postMessage({{type: 'confirmModal'}}, '*');
            }};
            document.getElementById('modal_cancel_btn').onclick = () => {{
                window.parent.postMessage({{type: 'cancelModal'}}, '*');
            }};
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
            /* All CSS styles would be contained here... */
        </style>
        """, unsafe_allow_html=True)

class SidebarRenderer:
    """Renders the sidebar UI"""
    
    @staticmethod
    def render():
        """Render sidebar components"""
        with st.sidebar:
            st.markdown('<div class="sidebar-header"><span>Chats</span></div>', unsafe_allow_html=True)
            st.button("➕ New Chat", on_click=ChatManager.create_new_chat, use_container_width=True, key="new_chat_button")
            st.markdown('<ul class="sidebar-history-list">', unsafe_allow_html=True)
            
            for chat in st.session_state.chat_history:
                SidebarRenderer._render_chat_item(chat)
                
            st.markdown('</ul>', unsafe_allow_html=True)
            SidebarRenderer._handle_actions()

    @staticmethod
    def _render_chat_item(chat: Dict):
        """Render individual chat item in sidebar"""
        is_active = chat['id'] == st.session_state.current_chat_id
        active_class = "active" if is_active else ""
        
        col1, col2 = st.columns([0.8, 0.2])
        
        with col1:
            st.markdown(f"""
                <div class="sidebar-history-item {active_class}" 
                     style="margin-bottom:0 !important; border:none !important; background:none !important;">
                    <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                    <span class="chat-title">{chat['title']}</span>
                </div>
            """, unsafe_allow_html=True)
            st.button(" ", key=f"load_chat_{chat['id']}", 
                     on_click=ChatManager.set_current_chat, args=(chat['id'],), 
                     use_container_width=True)

        with col2:
            action = st.selectbox(
                "Actions", ["", "Rename", "Delete"],
                key=f"chat_actions_{chat['id']}",
                label_visibility="collapsed"
            )
            if action:
                SidebarRenderer._handle_chat_action(chat, action)

    @staticmethod
    def _handle_chat_action(chat: Dict, action: str):
        """Process chat action selection"""
        st.session_state.action_target_chat_id = chat['id']
        st.session_state.action_type = action.lower()
        
        if action == "Delete":
            ModalManager.show(
                "Confirm Deletion",
                f'Are you sure you want to delete "{chat["title"]}"? This action cannot be undone.',
                lambda: ChatManager.delete_chat(chat['id'])
            )
            
        st.rerun()

    @staticmethod
    def _handle_actions():
        """Handle rename/delete actions in sidebar"""
        if not st.session_state.action_target_chat_id or st.session_state.action_type != "rename":
            return
            
        chat = next(
            (c for c in st.session_state.chat_history 
             if c['id'] == st.session_state.action_target_chat_id), 
            None
        )
        
        if not chat:
            return
            
        st.sidebar.subheader(f"Rename '{chat['title']}'")
        new_title = st.sidebar.text_input("New chat title:", value=chat['title'], 
                                         key=f"rename_input_{chat['id']}")
        
        col_save, col_cancel = st.sidebar.columns(2)
        with col_save:
            if st.button("Save", key=f"save_rename_{chat['id']}"):
                ChatManager.rename_chat(chat['id'], new_title)
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key=f"cancel_rename_{chat['id']}"):
                st.session_state.action_target_chat_id = None
                st.session_state.action_type = None
                st.rerun()

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
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    @staticmethod
    def _render_typing_indicator():
        """Render typing indicator placeholder"""
        if not st.session_state.typing_indicator_placeholder:
            st.session_state.typing_indicator_placeholder = st.empty()

class UserInputHandler:
    """Handles user input and bot responses"""
    
    @staticmethod
    def handle():
        """Process user input and generate responses"""
        if user_input := st.chat_input("Type your message...", key="main_chat_input"):
            UserInputHandler._process_user_input(user_input)

    @staticmethod
    def _process_user_input(user_input: str):
        """Process user input and generate bot response"""
        # Add user message
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
            
        # Simulate processing
        time.sleep(1.5)
        
        # Generate bot response
        bot_response = f"I received: '{user_input}'. This is a simulated response. In a real implementation, I would process your query."
        ChatManager.add_message("assistant", bot_response)
        
        # Clear typing indicator
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
    
    # Handle modal interactions
    if st.session_state.get('confirmModal'):
        if st.session_state.modal_confirm_callback:
            st.session_state.modal_confirm_callback()
        ModalManager.hide()
        st.rerun()
        
    elif st.session_state.get('cancelModal'):
        ModalManager.hide()
        st.rerun()

# ================ ENTRY POINT ================
if __name__ == "__main__":
    # JavaScript message handler for modal
    st.markdown("""
    <script>
        window.addEventListener('message', (event) => {
            if (event.data.type === 'confirmModal') {
                Streamlit.setComponentValue({confirmModal: true});
            }
            else if (event.data.type === 'cancelModal') {
                Streamlit.setComponentValue({cancelModal: true});
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    main()
