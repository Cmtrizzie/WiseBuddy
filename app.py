import streamlit as st
import time
from datetime import datetime

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"id": "3", "title": "Project X Summary", "time": "09:15"},
        {"id": "2", "title": "AI Ethics Discussion", "time": "Yesterday"},
        {"id": "1", "title": "Hello", "time": "18:48"}
    ]

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# Page configuration
st.set_page_config(
    page_title="WiseBuddy",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background-color: #fafafa;
    }
    
    /* Conversation items */
    .conversation-item {
        padding: 10px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 14px;
        color: #333333;
    }
    
    .conversation-item:hover {
        background-color: #f0f0f0;
    }
    
    .conversation-item.active {
        background-color: #e3f2fd;
        border-left: 3px solid #1976d2;
    }
    
    .conversation-time {
        font-size: 0.75rem;
        color: #666666;
        margin-top: 2px;
    }
    
    /* Profile section */
    .profile-section {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 20%;
        padding: 12px 16px;
        background: #ffffff;
        border-top: 1px solid #e0e0e0;
    }
    
    .profile-content {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        padding: 8px;
        border-radius: 8px;
        transition: background-color 0.2s;
    }
    
    .profile-content:hover {
        background-color: #f5f5f5;
    }
    
    .profile-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: #1976d2;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 16px;
    }
    
    /* Settings modal */
    .settings-modal {
        position: fixed;
        bottom: 80px;
        left: 20px;
        width: 18%;
        background: white;
        border-radius: 12px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        padding: 0;
        z-index: 100;
        border: 1px solid #e0e0e0;
        overflow: hidden;
        display: block;
    }
    
    .settings-header {
        padding: 20px;
        background: #f5f7fa;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .settings-body {
        padding: 0;
    }
    
    .settings-item {
        padding: 14px 20px;
        cursor: pointer;
        transition: background-color 0.2s;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .settings-item:hover {
        background-color: #f9f9f9;
    }
    
    .settings-item-title {
        font-weight: 500;
        color: #333;
    }
    
    .settings-item-subtitle {
        font-size: 0.85rem;
        color: #666;
    }
    
    .settings-footer {
        padding: 16px 20px;
        text-align: center;
        border-top: 1px solid #f0f0f0;
    }
    
    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        padding: 8px 12px;
    }
    
    .stChatFloatingInputContainer {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    
    /* Header */
    .chat-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript to handle profile click and settings
settings_js = """
<script>
// Function to handle profile click
function handleProfileClick() {
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: "profileClick"
    }, "*");
}

// Function to handle settings item clicks
function handleSettingsClick(item) {
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: "settingsItem",
        data: item
    }, "*");
}

// Attach click handler to profile
document.addEventListener("DOMContentLoaded", function() {
    const profile = document.querySelector(".profile-content");
    if (profile) {
        profile.onclick = handleProfileClick;
    }
    
    // Attach click handlers to settings items
    const settingsItems = document.querySelectorAll(".settings-item");
    settingsItems.forEach(item => {
        item.onclick = function() {
            handleSettingsClick(this.getAttribute("data-value"));
        };
    });
});
</script>
"""

st.components.v1.html(settings_js)

# Handle profile click
if st.session_state.get("profile_clicked"):
    st.session_state.show_settings = not st.session_state.show_settings
    st.session_state.profile_clicked = False
    st.rerun()

# Handle settings item clicks
if st.session_state.get("settings_item"):
    item = st.session_state.settings_item
    st.toast(f"Selected: {item.replace('_', ' ').title()}")
    if item == "logout":
        st.session_state.show_settings = False
        st.toast("You have been logged out", icon="🔒")
    st.session_state.settings_item = None

# Sidebar - Conversation History
with st.sidebar:
    st.title("Chats")
    
    # New chat button
    if st.button("+ New Chat", use_container_width=True, type="primary"):
        new_chat_id = str(len(st.session_state.conversation_history) + 1)
        st.session_state.conversation_history.insert(0, {
            "id": new_chat_id,
            "title": "New Chat",
            "time": datetime.now().strftime("%H:%M")
        })
        st.session_state.messages = []
        st.rerun()
    
    # Conversation history list (newest first)
    for conv in st.session_state.conversation_history:
        is_active = not st.session_state.messages and conv["id"] == str(len(st.session_state.conversation_history))
        st.markdown(
            f'<div class="conversation-item {"active" if is_active else ""}">'
            f'<div>{conv["title"]}</div>'
            f'<div class="conversation-time">{conv["time"]}</div>'
            '</div>',
            unsafe_allow_html=True
        )
    
    # Profile section
    st.markdown(
        """
        <div class="profile-section">
            <div class="profile-content">
                <div class="profile-avatar">U</div>
                <div>
                    <div style="font-weight: 500; color: #333;">User</div>
                    <div style="font-size: 0.8rem; color: #666;">Active now</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Settings modal
    if st.session_state.show_settings:
        st.markdown(
            """
            <div class="settings-modal">
                <div class="settings-header">
                    <div style="font-weight: 600; font-size: 1.1rem;">User Profile</div>
                    <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">user@example.com</div>
                </div>
                
                <div class="settings-body">
                    <div class="settings-item" data-value="profile">
                        <div class="settings-item-title">Profile</div>
                        <div class="settings-item-subtitle">Update your personal information</div>
                    </div>
                    
                    <div class="settings-item" data-value="account">
                        <div class="settings-item-title">Account</div>
                        <div class="settings-item-subtitle">Manage your subscription</div>
                    </div>
                    
                    <div class="settings-item" data-value="data_controller">
                        <div class="settings-item-title">Data Controller</div>
                        <div class="settings-item-subtitle">Manage your data preferences</div>
                    </div>
                    
                    <div class="settings-item" data-value="security">
                        <div class="settings-item-title">Security</div>
                        <div class="settings-item-subtitle">Password and authentication</div>
                    </div>
                    
                    <div class="settings-item" data-value="appearance">
                        <div class="settings-item-title">Appearance</div>
                        <div class="settings-item-subtitle">Theme and display settings</div>
                    </div>
                    
                    <div class="settings-item" data-value="about">
                        <div class="settings-item-title">About</div>
                        <div class="settings-item-subtitle">App version and information</div>
                    </div>
                </div>
                
                <div class="settings-footer">
                    <div class="settings-item" data-value="logout" style="color: #d32f2f; border-bottom: none;">
                        <div class="settings-item-title">Logout</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Main chat area
st.markdown(
    """
    <div class="chat-header">
        <div style="font-size: 28px;">💡</div>
        <h1 style="margin:0; color: #333;">WiseBuddy</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "💡"):
        st.markdown(message["content"])
        st.markdown(f'<div style="font-size: 0.75rem; color: #666; margin-top: 4px;">{message["time"]}</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask WiseBuddy anything..."):
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt, 
        "time": timestamp
    })
    
    # Update conversation title if first message
    if len(st.session_state.messages) == 1:
        st.session_state.conversation_history[0]["title"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
        st.session_state.conversation_history[0]["time"] = timestamp
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.markdown(f'<div style="font-size: 0.75rem; color: #666; margin-top: 4px;">{timestamp}</div>', unsafe_allow_html=True)

    # Generate bot response
    with st.chat_message("assistant", avatar="💡"):
        response_container = st.empty()
        simulated_response = f"Let me think about '{prompt.split()[0]}'... Here's what I've gathered:"
        
        # Simulated typing effect
        full_response = ""
        for word in simulated_response.split():
            full_response += word + " "
            response_container.markdown(full_response + "▌")
            time.sleep(0.08)
        
        response_container.markdown(full_response)
        st.markdown(f'<div style="font-size: 0.75rem; color: #666; margin-top: 4px;">{timestamp}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response, 
            "time": timestamp
        })

# Handle messages from JavaScript
def handle_js_message(message):
    if message.type == "profileClick":
        st.session_state.profile_clicked = True
        st.rerun()
    elif message.type == "settingsItem":
        st.session_state.settings_item = message.data
        st.rerun()

# Register the message handler
ctx = st.runtime.scriptrunner.get_script_run_ctx()
if ctx:
    session_id = ctx.session_id
    from streamlit.report_thread import get_report_ctx
    from streamlit.server.server import Server
    session_info = Server.get_current()._get_session_info(session_id)
    if session_info:
        session = session_info.session
        session._handle_js_message = handle_js_message
