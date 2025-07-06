import streamlit as st
import random
import time
from datetime import datetime

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = random.randint(1000, 9999)

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
    
    /* User messages */
    [data-testid="stChatMessage"]:has(.st-emotion-cache-4oy321) {
        justify-content: flex-end;
    }
    
    /* Bot messages */
    [data-testid="stChatMessage"]:has(.st-emotion-cache-1c7y2kd) {
        justify-content: flex-start;
    }
    
    /* Message bubbles */
    .stChatMessage {
        padding: 12px 16px;
        border-radius: 18px;
        margin-bottom: 8px;
        max-width: 80%;
    }
    
    /* User bubble */
    .st-emotion-cache-4oy321 {
        background-color: #0f6cbf;
        color: white;
        border-bottom-right-radius: 2px !important;
    }
    
    /* Bot bubble */
    .st-emotion-cache-1c7y2kd {
        background-color: #f0f2f6;
        color: #333;
        border-bottom-left-radius: 2px !important;
    }
    
    /* Timestamps */
    .message-time {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 4px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4a00e0, #8e2de2);
        color: white;
    }
    
    /* Download button */
    .stDownloadButton {
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🤖 ChatBot Pro")
    st.subheader(f"Conversation #{st.session_state.conversation_id}")
    
    st.divider()
    st.markdown("### Features")
    st.markdown("- Natural conversation flow")
    st.markdown("- Contextual memory")
    st.markdown("- Response streaming")
    st.markdown("- Export history")
    
    st.divider()
    st.markdown("### Settings")
    bot_personality = st.selectbox(
        "Bot Personality",
        ["Friendly Assistant", "Professional Advisor", "Technical Expert", "Casual Buddy"]
    )
    
    st.divider()
    if st.button("New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = random.randint(1000, 9999)
        st.rerun()
    
    # Export chat history
    if st.button("Export Conversation", use_container_width=True):
        chat_text = f"Conversation #{st.session_state.conversation_id}\n\n"
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            chat_text += f"{role} ({msg['time']}):\n{msg['content']}\n\n"
        
        st.download_button(
            label="Download History",
            data=chat_text,
            file_name=f"chat_history_{st.session_state.conversation_id}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Main chat area
st.title(f"ChatBot Pro - {bot_personality}")
st.caption(f"Conversation ID: #{st.session_state.conversation_id}")

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
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.caption(f"{timestamp} • User")

    # Generate bot response (simulated)
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        simulated_response = ""
        
        # Simulated response based on personality
        responses = {
            "Friendly Assistant": [
                "Great question! Let me think about that...",
                "I'm happy to help with that!",
                "That's an interesting point. Here's what I know..."
            ],
            "Professional Advisor": [
                "Based on my analysis, I recommend...",
                "The optimal approach would be...",
                "After reviewing available data, my assessment is..."
            ],
            "Technical Expert": [
                "From a technical perspective...",
                "The underlying mechanism works as follows...",
                "Considering the technical constraints..."
            ],
            "Casual Buddy": [
                "Oh cool! So here's the deal...",
                "I was just thinking about that too!",
                "Haha, interesting! Let me tell you..."
            ]
        }
        
        # Start with a personality-specific intro
        intro = random.choice(responses[bot_personality])
        simulated_response += intro + " "
        
        # Generate core response
        topics = prompt.split()[:5]
        core_response = f"Regarding {', '.join(topics)}... " + " ".join(
            [f"Lorem ipsum dolor sit amet {random.choice(['consectetur', 'adipiscing', 'elit'])}. "
             for _ in range(random.randint(3, 6))]
        )
        
        # Generate conclusion
        conclusions = [
            "Hope that helps!",
            "Let me know if you need more details.",
            "What else can I assist with?",
            "Does that answer your question?"
        ]
        conclusion = random.choice(conclusions)
        
        full_response = intro + " " + core_response + " " + conclusion
        
        # Simulate streaming response
        for chunk in full_response.split():
            simulated_response += chunk + " "
            response_container.markdown(simulated_response + "▌")
            time.sleep(0.08)  # Adjust speed here
        
        # Display final message
        response_container.markdown(simulated_response)
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.caption(f"{timestamp} • Assistant")
        
        # Add to session state
        st.session_state.messages.append({
            "role": "assistant", 
            "content": simulated_response, 
            "time": timestamp
        })
