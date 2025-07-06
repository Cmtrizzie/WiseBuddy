import streamlit as st
import time
from datetime import datetime

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"id": "3", "title": "Quantum Physics Learning", "time": "10:30"},
        {"id": "2", "title": "Project X Summary", "time": "09:15"},
        {"id": "1", "title": "AI Ethics Discussion", "time": "Yesterday"}
    ]

# Page configuration
st.set_page_config(
    page_title="WiseBuddy",
    page_icon="💡",  # Lightbulb icon for wisdom
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Conversation items */
    .conversation-item {
        padding: 10px 15px;
        margin: 6px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 14px;
    }
    
    .conversation-item:hover {
        background-color: #f5f5f5;
    }
    
    .conversation-item.active {
        background-color: #ebf5ff;
        border-left: 3px solid #0068c9;
    }
    
    .conversation-time {
        font-size: 0.75rem;
        color: #666;
        margin-top: 2px;
    }
    
    /* Profile section */
    .profile-section {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 20%;
        padding: 15px;
        background: white;
        border-top: 1px solid #e0e0e0;
    }
    
    .profile-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .profile-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #0068c9;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    
    /* Main chat header */
    .chat-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .chat-header-icon {
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Conversation History
with st.sidebar:
    st.title("Chats")
    
    # Add new conversation button at top
    if st.button("+ New Chat", use_container_width=True, type="primary"):
        new_chat_id = str(len(st.session_state.conversation_history) + 1)
        st.session_state.conversation_history.insert(0, {
            "id": new_chat_id,
            "title": "New Conversation",
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
    
    # Fixed profile section at bottom
    st.markdown(
        """
        <div class="profile-section">
            <div class="profile-content">
                <div class="profile-avatar">U</div>
                <div>
                    <div style="font-weight: bold;">User</div>
                    <div style="font-size: 0.8rem; color: #666;">Active now</div>
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
        <div class="chat-header-icon">💡</div>
        <h1 style="margin:0;">WiseBuddy</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "💡"):
        st.markdown(message["content"])
        st.markdown(f'<div class="conversation-time">{message["time"]}</div>', unsafe_allow_html=True)

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
        st.session_state.conversation_history[0]["title"] = prompt[:25] + ("..." if len(prompt) > 25 else "")
        st.session_state.conversation_history[0]["time"] = timestamp
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.markdown(f'<div class="conversation-time">{timestamp}</div>', unsafe_allow_html=True)

    # Generate bot response
    with st.chat_message("assistant", avatar="💡"):
        response_container = st.empty()
        simulated_response = f"WiseBuddy here! Regarding '{prompt.split()[0]}', my thoughts are..."
        
        # Simulated typing effect
        full_response = ""
        for word in simulated_response.split():
            full_response += word + " "
            response_container.markdown(full_response + "▌")
            time.sleep(0.08)
        
        response_container.markdown(full_response)
        st.markdown(f'<div class="conversation-time">{timestamp}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response, 
            "time": timestamp
        })
