import streamlit as st
import random
import time
from datetime import datetime

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = random.randint(1000, 9999)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = {
        "1001": "AI Ethics Discussion",
        "1002": "Project X Summary",
        "1003": "Quantum Physics Learning",
        str(st.session_state.conversation_id): "Current Chat"
    }

# Page configuration
st.set_page_config(
    page_title="ChatBot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main chat container */
    .stChatFloatingInputContainer {
        border-radius: 20px;
        padding: 20px;
    }
    
    /* Sidebar conversation items */
    .conversation-item {
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .conversation-item:hover {
        background-color: #f0f2f6;
    }
    
    .conversation-item.active {
        background-color: #e6f7ff;
        border-left: 3px solid #0f6cbf;
    }
    
    /* Profile section */
    .profile-section {
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Conversation History
with st.sidebar:
    st.title("Chats")
    
    # Conversation history list
    for conv_id, title in st.session_state.conversation_history.items():
        is_active = str(conv_id) == str(st.session_state.conversation_id)
        st.markdown(
            f'<div class="conversation-item {"active" if is_active else ""}">'
            f'<strong>{title}</strong><br>'
            f'<small>ID: {conv_id}</small>'
            '</div>',
            unsafe_allow_html=True
        )
    
    # Profile section
    st.markdown('<div class="profile-section">', unsafe_allow_html=True)
    st.subheader("Profile")
    
    # Profile settings
    bot_personality = st.selectbox(
        "Bot Personality",
        ["Friendly Assistant", "Professional Advisor", "Technical Expert", "Casual Buddy"],
        key="personality_select"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat area
st.title(f"ChatBot Pro - {bot_personality}")
st.caption(f"Conversation ID: #{st.session_state.conversation_id} • {st.session_state.conversation_history[str(st.session_state.conversation_id)]}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])
        st.caption(f"{message['time']} • {message['role'].capitalize()}")

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt, 
        "time": timestamp
    })
    
    # Update conversation title if first message
    if len(st.session_state.messages) == 1:
        st.session_state.conversation_history[str(st.session_state.conversation_id)] = prompt[:30] + ("..." if len(prompt) > 30 else "")
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.caption(f"{timestamp} • User")

    # Generate bot response
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        simulated_response = ""
        
        # Simulated typing effect
        responses = {
            "Friendly Assistant": "That's an interesting question! Let me think...",
            "Professional Advisor": "After careful consideration, my analysis suggests...",
            "Technical Expert": "From a technical perspective, the answer involves...",
            "Casual Buddy": "Oh cool! So here's what I know about that..."
        }
        
        intro = responses[bot_personality]
        
        for chunk in intro.split():
            simulated_response += chunk + " "
            response_container.markdown(simulated_response + "▌")
            time.sleep(0.1)
        
        response_container.markdown(simulated_response)
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.caption(f"{timestamp} • Assistant")
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": simulated_response, 
            "time": timestamp
        })
