import streamlit as st
import google.generativeai as genai
import random

# 👉 Configure your Gemini API Key
genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your actual API key
model = genai.GenerativeModel('gemini-1.5-flash')

# 👉 Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy �", page_icon="🤖", layout="centered")

# 👉 CSS Styling (Bubbles + Background + Shadows)
st.markdown("""
    <style>
    body {
        background-color: #f7f9fc;
        font-family: Arial, sans-serif;
    }
    .big-font { 
        font-size:26px !important; 
        font-weight:bold; 
        color:#2c3e50; 
    }
    .user-bubble {
        background-color:#d1e7dd;
        padding:12px 15px;
        border-radius:18px 18px 0 18px;
        max-width:70%;
        font-size:16px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-left: auto;
    }
    .bot-bubble {
        background-color:#fff3cd;
        padding:12px 15px;
        border-radius:18px 18px 18px 0;
        max-width:70%;
        font-size:16px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-right: auto;
    }
    .error-bubble {
        background-color:#f8d7da;
        padding:12px 15px;
        border-radius:18px 18px 18px 0;
        max-width:70%;
        font-size:16px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-right: auto;
    }
    .chat-container {
        padding-bottom: 70px;
    }
    .stChatInput {
        position: fixed;
        bottom: 20px;
        width: 70%;
        left: 15%;
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 👉 Title + Quote
st.markdown('<p class="big-font">💬 Welcome to <span style="color:#6c63ff;">WiseBuddy</span> 🧠</p>', unsafe_allow_html=True)
quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now."
]
st.markdown(f'<div style="background-color:#e6e6fa;padding:10px;border-radius:10px;text-align:center;margin-bottom:20px;"><em>{random.choice(quotes)}</em></div>', unsafe_allow_html=True)

# 👉 Initialize Chat State
if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_category' not in st.session_state:
    st.session_state.current_category = "🌟 Motivation & Positivity"

# 👉 Category Select
def update_category():
    st.session_state.current_category = st.session_state.category_select

category = st.selectbox(
    "📝 Choose your advice style:",
    options=[
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace"
    ],
    index=0,
    key="category_select",
    on_change=update_category
)

# 👉 Clear Chat
if st.button("🗑️ Clear Chat"):
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.history = []
    st.session_state.current_category = category
    st.rerun()

# 👉 Chat Display
chat_container = st.container()
with chat_container:
    for speaker, message in st.session_state.history:
        if speaker == "user":
            # User message - aligned right with avatar on right
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                    <div style="display: flex; align-items: center; gap: 8px; max-width: 85%;">
                        <div class="user-bubble">
                            <strong>You:</strong><br>
                            {message}
                        </div>
                        <div style="font-size:24px;">🧑</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif speaker == "error":
            # Error message - aligned left with warning icon
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                    <div style="display: flex; align-items: center; gap: 8px; max-width: 85%;">
                        <div style="font-size:24px;">⚠️</div>
                        <div class="error-bubble">
                            <strong>Error:</strong><br>
                            {message}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Bot message - aligned left with bot avatar
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                    <div style="display: flex; align-items: center; gap: 8px; max-width: 85%;">
                        <div style="font-size:24px;">🤖</div>
                        <div class="bot-bubble">
                            <strong>WiseBuddy:</strong><br>
                            {message}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# 👉 User Input
user_input = st.chat_input("💭 Type your message here...")

# 👉 Generate Response
if user_input:
    st.session_state.history.append(("user", user_input))
    
    try:
        # Create prompt with category context
        prompt = f"""You are WiseBuddy, a friendly advice chatbot specializing in {st.session_state.current_category}. 
        Respond to the user in a kind, supportive manner. Keep responses concise (1-2 paragraphs max).
        
        User: {user_input}"""
        
        with st.spinner("🤖 WiseBuddy is thinking..."):
            response = st.session_state.chat.send_message(prompt)
            bot_response = response.text
            st.session_state.history.append(("bot", bot_response))
            
    except Exception as e:
        error_msg = f"Sorry, I'm having trouble responding right now. Please try again later. ({str(e)})"
        st.session_state.history.append(("error", error_msg))
    
    st.rerun()
