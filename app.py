import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Set page config
st.set_page_config(page_title="Gemini 1.5 Flash Chatbot", page_icon="🚀")

# Initialize Gemini with your API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # Store key in Streamlit secrets

# Initialize the model (cached for performance)
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You're a helpful assistant. Respond concisely and conversationally."
    )

model = load_model()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Gemini Flash assistant. How can I help?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Your message..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Generate response with streaming
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Convert history to Gemini format
        history = []
        for msg in st.session_state.messages[:-1]:  # Exclude current prompt
            history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })
        
        # Generate response
        response = model.generate_content(
            contents=history + [{"role": "user", "parts": [prompt]}],
            stream=True
        )
        
        # Stream the response
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # Add assistant response to history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )

# Sidebar controls
with st.sidebar:
    st.title("Gemini 1.5 Flash Chatbot")
    st.caption(f"Using model: gemini-1.5-flash")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I help?"}
        ]
        st.rerun()
    
    st.divider()
    st.write("Current conversation:")
    for i, msg in enumerate(st.session_state.messages):
        prefix = "🤖" if msg["role"] == "assistant" else "👤"
        st.text(f"{prefix} {msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''}")
