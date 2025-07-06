import streamlit as st
import random
import time
from datetime import datetime

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = {
        "1": "AI Ethics Discussion",
        "2": "Project X Summary",
        "3": "Quantum Physics Learning",
        "4": "Current Chat"
    }

# Page configuration
st.set_page_config(
    page_title="Chat App",
    page_icon="💬",
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
    
    /* Profile section */
    .profile-section {
        margin-top: auto;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Timestamps */
    .message-time {
        font-size: 0.75rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Conversation History
with st.sidebar:
    st.title("Chats")
    
    # Conversation history list
    for conv_id, title in st.session_state.conversation_history.items():
        is_active = conv_id == "4"  # Current chat
        st.markdown(
            f'<div class="conversation-item {"active" if is_active else ""}">'
            f'{title}'
            '</div>',
            unsafe_allow_html=True
        )
    
    # Minimal profile section
    st.markdown('<div class="profile-section">', unsafe_allow_html=True)
    st.write("Signed in as **User**")
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat area
st.title("Current Conversation")
st.caption("Discussion about various topics")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])
        st.markdown(f'<div class="message-time">{message["time"]}</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt, 
        "time": timestamp
    })
    
    # Update conversation title if first message
    if len(st.session_state.messages) == 1:
        st.session_state.conversation_history["4"] = prompt[:25] + ("..." if len(prompt) > 25 else "")
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.markdown(f'<div class="message-time">{timestamp}</div>', unsafe_allow_html=True)

    # Generate bot response
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        simulated_response = "Here's a response to your message about " + prompt.split()[0].lower() + "..."
        
        # Simulated typing effect
        full_response = ""
        for word in simulated_response.split():
            full_response += word + " "
            response_container.markdown(full_response + "▌")
            time.sleep(0.08)
        
        response_container.markdown(full_response)
        timestamp = datetime.now().strftime("%H:%M")
        st.markdown(f'<div class="message-time">{timestamp}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response, 
            "time": timestamp
        })
