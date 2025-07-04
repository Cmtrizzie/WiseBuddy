import streamlit as st
import google.generativeai as genai
import random

# 👉 Configure your actual Gemini API key
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")
model = genai.GenerativeModel('gemini-1.5-flash')

# 👉 Streamlit page setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 CSS Styling
st.markdown("""
    <style>
    .big-font { font-size:26px !important; font-weight:bold; color:#2c3e50; }
    .advice-box { background-color:#fff; padding:15px; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1); color:#333; font-size:17px; margin-top:10px; }
    .user-bubble { background-color:#d1e7dd; padding:12px 15px; border-radius:15px; max-width:70%; font-size:16px; margin-left:auto; }
    .bot-bubble { background-color:#fff3cd; padding:12px 15px; border-radius:15px; max-width:70%; font-size:16px; margin-right:auto; }
    .chat-container { display:flex; flex-direction:column; gap:10px; margin-top:10px; }
    </style>
""", unsafe_allow_html=True)

# 👉 Title + Quote of the Day
st.markdown('<p class="big-font">💬 Welcome to <span style="color:#6c63ff;">WiseBuddy</span> 🧠</p>', unsafe_allow_html=True)

quotes = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Success is the sum of small efforts repeated daily.",
    "💡 The best way to predict the future is to create it.",
    "❤️ You are stronger than you think.",
    "🔥 Dream big. Start small. Act now."
]
st.markdown(f'<div style="background-color:#e6e6fa;padding:10px;border-radius:10px;text-align:center;"><em>{random.choice(quotes)}</em></div>', unsafe_allow_html=True)

# 👉 Initialize Chat History and Category
if 'chat' not in st.session_state:
    st.session_state.chat = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_category' not in st.session_state:
    st.session_state.current_category = "🌟 Motivation & Positivity"

# 👉 Category Select with persistence
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
    index=[
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace"
    ].index(st.session_state.current_category),
    key="category_select",
    on_change=update_category
)

# 👉 Clear Chat Button
if st.button("🗑️ Clear Chat"):
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.history = []
    st.session_state.current_category = category

# Initialize chat if not exists
if st.session_state.chat is None:
    st.session_state.chat = model.start_chat(history=[])

# 👉 Display Chat History
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for speaker, message in st.session_state.history:
        if speaker == "user":
            st.markdown(f'''
                <div class="user-bubble">
                    <strong>You:</strong><br>{message}
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="bot-bubble">
                    <strong>WiseBuddy 🤖:</strong><br>{message}
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 👉 User Input
user_input = st.chat_input("💭 Type your message here:")

# 👉 Process User Input
if user_input:
    # Add user message to history
    st.session_state.history.append(("user", user_input))
    
    # Generate context-aware prompt
    prompt = f"""
    You are WiseBuddy, a friendly advice chatbot specializing in {st.session_state.current_category}. 
    The user has been chatting with you about: {st.session_state.history[-2][1] if len(st.session_state.history) > 1 else 'new conversation'}
    
    Respond kindly and helpfully to: {user_input}
    """
    
    with st.spinner("WiseBuddy is thinking..."):
        # Send message and get response
        response = st.session_state.chat.send_message(prompt)
        bot_response = response.text
        
        # Add bot response to history
        st.session_state.history.append(("bot", bot_response))
    
    # Rerun to update chat display
    st.rerun()
