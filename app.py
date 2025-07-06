import streamlit as st
import time
import uuid
from typing import List, Dict, Optional, Callable, Tuple

# ================ CONSTANTS & CONFIGURATION ================
PRIMARY_COLOR = "#5a7d9a"
ACCENT_COLOR = "#8cabc2"
BACKGROUND_COLOR = "#f0f2f5"
SIDEBAR_BG_COLOR = "#3f5e82"
TEXT_COLOR_LIGHT = "#ffffff"
CONTEXT_MENU_BG = "#2a4058"

# Configure Streamlit page
st.set_page_config(
    page_title="WiseBuddy Chatbot",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None
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
            "context_menu": {"active": False, "chat_id": None, "position": (0, 0)},
            "rename_chat_id": None,
            "delete_chat_id": None,
            "sidebar_expanded": True,
            "show_modal": False,
            "modal_title": "",
            "modal_message": "",
            "modal_confirm_callback": None,
            "typing_indicator_placeholder": None,
            "long_press_timer": None,
            "touch_start_time": 0
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
                'title': 'Project Planning',
                'icon': 'tasks',
                'messages': [
                    {"role": "assistant", "content": "Hello! I'm WiseBuddy, your intelligent assistant. How can I help with your project planning?"},
                    {"role": "user", "content": "What are the key milestones we should set?"},
                    {"role": "assistant", "content": "Key milestones include: 1. Requirements gathering 2. Design phase 3. Development 4. Testing 5. Deployment"},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Technical Research',
                'icon': 'microscope',
                'messages': [
                    {"role": "assistant", "content": "Welcome to our technical research discussion."},
                    {"role": "user", "content": "What are the latest trends in AI?"},
                    {"role": "assistant", "content": "Current trends include transformer architectures, few-shot learning, and ethical AI frameworks."},
                ]
            },
            # Additional sample chats...
        ]

# ================ CHAT MANAGEMENT FUNCTIONS ================
class ChatManager:
    """Handles chat-related operations and data management"""
    
    @staticmethod
    def get_chat(chat_id: str) -> Optional[Dict]:
        """Get chat by ID"""
        for chat in st.session_state.chat_history:
            if chat['id'] == chat_id:
                return chat
        return None

    @staticmethod
    def get_current_chat() -> Optional[Dict]:
        """Get the current active chat"""
        return ChatManager.get_chat(st.session_state.current_chat_id)

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
        
        # Close context menu if open
        st.session_state.context_menu["active"] = False

    @staticmethod
    def set_current_chat(chat_id: str):
        """Set the active chat"""
        st.session_state.current_chat_id = chat_id
        st.session_state.context_menu["active"] = False

    @staticmethod
    def rename_chat(chat_id: str, new_title: str):
        """Rename a chat session"""
        if not new_title.strip():
            return
            
        chat = ChatManager.get_chat(chat_id)
        if chat and new_title != chat['title']:
            chat['title'] = new_title
            if chat_id == st.session_state.current_chat_id:
                ChatManager.add_message(
                    "assistant", 
                    f"Chat renamed to: **{new_title}**"
                )
        
        st.session_state.rename_chat_id = None

    @staticmethod
    def delete_chat(chat_id: str):
        """Delete a chat session"""
        chat_to_delete = ChatManager.get_chat(chat_id)
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
            
        st.session_state.delete_chat_id = None

# ================ SIDEBAR COMPONENT ================
class ProfessionalSidebar:
    """Implements a professional sidebar with enhanced functionality"""
    
    @staticmethod
    def render():
        """Render the sidebar with all components"""
        with st.sidebar:
            # Sidebar header with toggle button
            ProfessionalSidebar._render_header()
            
            # Always-visible New Chat button
            ProfessionalSidebar._render_new_chat_button()
            
            # Chat history list
            ProfessionalSidebar._render_chat_list()
            
            # Context menu for chat actions
            ProfessionalSidebar._render_context_menu()
            
            # Rename input when needed
            ProfessionalSidebar._render_rename_input()
            
            # Mobile sidebar toggle overlay
            ProfessionalSidebar._render_mobile_overlay()

    @staticmethod
    def _render_header():
        """Render sidebar header with toggle button"""
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.markdown(f'<div style="font-size:1.2em; font-weight:600; color:{TEXT_COLOR_LIGHT}">Chat History</div>', 
                        unsafe_allow_html=True)
        with col2:
            # Toggle button for mobile
            if st.button("☰", key="sidebar_toggle", use_container_width=True):
                st.session_state.sidebar_expanded = not st.session_state.sidebar_expanded

    @staticmethod
    def _render_new_chat_button():
        """Render the always-visible New Chat button"""
        if st.button(
            "➕ New Chat", 
            use_container_width=True,
            key="new_chat_button",
            on_click=ChatManager.create_new_chat
        ):
            st.session_state.context_menu["active"] = False

    @staticmethod
    def _render_chat_list():
        """Render the list of chat history items"""
        st.markdown('<div class="sidebar-history-list">', unsafe_allow_html=True)
        
        for chat in st.session_state.chat_history:
            is_active = chat['id'] == st.session_state.current_chat_id
            active_class = "active" if is_active else ""
            
            # Use columns for layout
            col1, col2 = st.columns([0.85, 0.15])
            
            with col1:
                # Chat item with touch/click handlers
                st.markdown(
                    f"""
                    <div class="sidebar-history-item {active_class}" 
                         id="chat_{chat['id']}" 
                         data-chat-id="{chat['id']}"
                         oncontextmenu="event.preventDefault(); handleContextMenu('{chat['id']}', event)">
                        <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                        <span class="chat-title">{chat['title']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Hidden button to handle chat selection
                st.button(
                    " ", 
                    key=f"load_chat_{chat['id']}", 
                    on_click=ChatManager.set_current_chat, 
                    args=(chat['id'],),
                    use_container_width=True
                )
            
            with col2:
                # Context menu trigger (visible only on desktop)
                if st.button("⋮", key=f"menu_trigger_{chat['id']}", use_container_width=True):
                    st.session_state.context_menu = {
                        "active": True,
                        "chat_id": chat['id'],
                        "position": (0, 0)  # Position will be set via JS
                    }
        
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _render_context_menu():
        """Render the context menu for chat actions"""
        if not st.session_state.context_menu["active"]:
            return
            
        chat_id = st.session_state.context_menu["chat_id"]
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return
            
        # Position the context menu dynamically
        pos_x, pos_y = st.session_state.context_menu["position"]
        position_style = f"position:fixed; top:{pos_y}px; left:{pos_x}px; z-index:1000;"
        
        st.markdown(
            f"""
            <div class="context-menu" style="{position_style}">
                <div class="context-menu-header">
                    <span>Chat Actions</span>
                    <button class="close-context-menu" onclick="closeContextMenu()">×</button>
                </div>
                <div class="context-menu-item" onclick="handleContextAction('{chat_id}', 'rename')">
                    <i class="fas fa-edit"></i> Rename
                </div>
                <div class="context-menu-item" onclick="handleContextAction('{chat_id}', 'delete')">
                    <i class="fas fa-trash"></i> Delete
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def _render_rename_input():
        """Render rename input when a chat is being renamed"""
        if not st.session_state.rename_chat_id:
            return
            
        chat = ChatManager.get_chat(st.session_state.rename_chat_id)
        if not chat:
            return
            
        with st.sidebar:
            st.subheader("Rename Chat")
            new_title = st.text_input(
                "New title:", 
                value=chat['title'],
                key=f"rename_input_{chat['id']}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", key=f"save_rename_{chat['id']}"):
                    ChatManager.rename_chat(chat['id'], new_title)
            with col2:
                if st.button("Cancel", key=f"cancel_rename_{chat['id']}"):
                    st.session_state.rename_chat_id = None

    @staticmethod
    def _render_mobile_overlay():
        """Render mobile overlay for sidebar toggle"""
        if st.session_state.sidebar_expanded:
            return
            
        st.markdown(
            """
            <div class="mobile-sidebar-overlay">
                <button class="sidebar-toggle-btn" onclick="toggleSidebar()">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )

# ================ UI STYLING & COMPONENTS ================
class UICustomizer:
    """Handles custom CSS and UI styling"""
    
    @staticmethod
    def inject_custom_css():
        """Inject custom CSS styles"""
        st.markdown(f"""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            /* Sidebar styling */
            [data-testid="stSidebar"] {{
                background-color: {SIDEBAR_BG_COLOR} !important;
                color: {TEXT_COLOR_LIGHT} !important;
                padding: 15px 10px !important;
                transition: transform 0.3s ease-in-out;
            }}
            
            .sidebar-history-list {{
                list-style-type: none !important;
                padding: 10px 0 !important;
                margin: 10px 0 !important;
                max-height: calc(100vh - 150px);
                overflow-y: auto;
            }}
            
            .sidebar-history-item {{
                display: flex;
                align-items: center;
                padding: 12px 15px;
                margin-bottom: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 0.95em;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {TEXT_COLOR_LIGHT};
            }}
            
            .sidebar-history-item:hover {{
                background-color: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }}
            
            .sidebar-history-item.active {{
                background-color: rgba(255, 255, 255, 0.25);
                font-weight: bold;
                border-color: rgba(255, 255, 255, 0.3);
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            
            .chat-history-icon {{
                margin-right: 10px;
                font-size: 14px;
                opacity: 0.9;
                width: 20px;
                text-align: center;
            }}
            
            /* Context menu styling */
            .context-menu {{
                background-color: {CONTEXT_MENU_BG};
                border-radius: 6px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
                padding: 5px 0;
                width: 180px;
                z-index: 1000;
            }}
            
            .context-menu-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                font-weight: 600;
                font-size: 0.9em;
            }}
            
            .close-context-menu {{
                background: none;
                border: none;
                color: {TEXT_COLOR_LIGHT};
                cursor: pointer;
                font-size: 1.2em;
                padding: 0 5px;
            }}
            
            .context-menu-item {{
                padding: 10px 15px;
                cursor: pointer;
                transition: background-color 0.2s;
                display: flex;
                align-items: center;
            }}
            
            .context-menu-item i {{
                margin-right: 10px;
                width: 20px;
            }}
            
            .context-menu-item:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            /* Mobile sidebar overlay */
            .mobile-sidebar-overlay {{
                position: fixed;
                top: 50%;
                left: 0;
                transform: translateY(-50%);
                z-index: 99;
                display: none;
            }}
            
            .sidebar-toggle-btn {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 0 12px 12px 0;
                width: 30px;
                height: 50px;
                cursor: pointer;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            }}
            
            /* Responsive behavior */
            @media (max-width: 768px) {{
                [data-testid="stSidebar"]:not([aria-expanded="true"]) {{
                    transform: translateX(-100%);
                }}
                
                [data-testid="stSidebar"][aria-expanded="true"] {{
                    transform: translateX(0);
                }}
                
                .mobile-sidebar-overlay {{
                    display: block;
                }}
            }}
        </style>
        
        <script>
            // Handle context menu display
            function handleContextMenu(chatId, event) {{
                const rect = event.target.getBoundingClientRect();
                const x = rect.right + 5;
                const y = rect.top;
                
                // Send position to Streamlit
                window.parent.postMessage({{
                    type: 'contextMenu',
                    chatId: chatId,
                    posX: x,
                    posY: y
                }}, '*');
            }}
            
            // Handle context menu actions
            function handleContextAction(chatId, action) {{
                window.parent.postMessage({{
                    type: 'contextAction',
                    chatId: chatId,
                    action: action
                }}, '*');
            }}
            
            // Close context menu
            function closeContextMenu() {{
                window.parent.postMessage({{type: 'closeContextMenu'}}, '*');
            }}
            
            // Toggle sidebar on mobile
            function toggleSidebar() {{
                window.parent.postMessage({{type: 'toggleSidebar'}}, '*');
            }}
            
            // Initialize touch events for long press
            document.addEventListener('touchstart', function(e) {{
                const chatItem = e.target.closest('.sidebar-history-item');
                if (chatItem) {{
                    window.touchStartTime = new Date().getTime();
                    window.longPressTimer = setTimeout(() => {{
                        const chatId = chatItem.dataset.chatId;
                        const rect = chatItem.getBoundingClientRect();
                        window.parent.postMessage({{
                            type: 'contextMenu',
                            chatId: chatId,
                            posX: rect.right + 5,
                            posY: rect.top
                        }}, '*');
                    }}, 500); // 500ms for long press
                }}
            }}, {{ passive: true }});
            
            document.addEventListener('touchend', function(e) {{
                if (window.longPressTimer) {{
                    clearTimeout(window.longPressTimer);
                    window.longPressTimer = null;
                }}
            }}, {{ passive: true }});
        </script>
        """, unsafe_allow_html=True)

# ================ MAIN APPLICATION ================
def main():
    """Main application entry point"""
    # Initialize state and UI
    SessionStateManager.initialize()
    UICustomizer.inject_custom_css()
    
    # Handle JavaScript messages
    if st.session_state.get("contextMenu"):
        data = st.session_state.contextMenu
        st.session_state.context_menu = {
            "active": True,
            "chat_id": data["chatId"],
            "position": (data["posX"], data["posY"])
        }
        st.session_state.contextMenu = None
        st.rerun()
    
    if st.session_state.get("contextAction"):
        data = st.session_state.contextAction
        if data["action"] == "rename":
            st.session_state.rename_chat_id = data["chatId"]
            st.session_state.context_menu["active"] = False
        elif data["action"] == "delete":
            st.session_state.delete_chat_id = data["chatId"]
            st.session_state.context_menu["active"] = False
        st.session_state.contextAction = None
        st.rerun()
    
    if st.session_state.get("closeContextMenu"):
        st.session_state.context_menu["active"] = False
        st.session_state.closeContextMenu = None
        st.rerun()
    
    if st.session_state.get("toggleSidebar"):
        st.session_state.sidebar_expanded = not st.session_state.sidebar_expanded
        st.session_state.toggleSidebar = None
        st.rerun()
    
    # Render the professional sidebar
    ProfessionalSidebar.render()
    
    # Main chat interface would be rendered here...

# ================ ENTRY POINT ================
if __name__ == "__main__":
    # JavaScript message handler
    st.markdown("""
    <script>
        window.addEventListener('message', (event) => {
            if (event.data.type === 'contextMenu') {
                Streamlit.setComponentValue({
                    contextMenu: {
                        chatId: event.data.chatId,
                        posX: event.data.posX,
                        posY: event.data.posY
                    }
                });
            }
            else if (event.data.type === 'contextAction') {
                Streamlit.setComponentValue({
                    contextAction: {
                        chatId: event.data.chatId,
                        action: event.data.action
                    }
                });
            }
            else if (event.data.type === 'closeContextMenu') {
                Streamlit.setComponentValue({closeContextMenu: true});
            }
            else if (event.data.type === 'toggleSidebar') {
                Streamlit.setComponentValue({toggleSidebar: true});
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    main()
