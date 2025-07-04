import streamlit as st
import google.generativeai as genai
import random

# 👉 Configure your Gemini API Key
genai.configure(api_key="YOUR_API_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')

# 👉 Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 CSS Styling (Bubbles + Background + Shadows)
st.markdown("""
    <style>
    body {
        background-color: #f7f9fc;
    }
    .big-font { font-size:26px !important; font-weight:bold; color:#2c3e50; }
    .chat-container { display:flex; flex-direction:column; gap:10px; margin-top:10px; }
    .user-bubble {
        background-color:#d1e7dd;
        padding:12px 15px;
        border-radius:15px;
        max-width:70%;
        font-size:16px;
        margin-left:auto;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .bot-bubble {
        background-color:#fff3cd;
        padding:12px 15px;
        border-radius:15px;
        max-width:70%;
        font-size:16px;
        margin-right:auto;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
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
st.markdown(f'<div style="background-color:#e6e6fa;padding:10px;border-radius:10px;text-align:center;"><em>{random.choice(quotes)}</em></div>', unsafe_allow_html=True)

# 👉 Initialize Chat State
if 'chat' not in st.session_state:
    st.session_state.chat = None
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
    index=[
        "🌟 Motivation & Positivity",
        "💡 Business & Wealth",
        "❤️ Love & Relationships",
        "🧘 Mindfulness & Peace"
    ].index(st.session_state.current_category),
    key="category_select",
    on_change=update_category
)

# 👉 Clear Chat
if st.button("🗑️ Clear Chat"):
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.history = []
    st.session_state.current_category = category

# 👉 Start Chat
if st.session_state.chat is None:
    st.session_state.chat = model.start_chat(history=[])

# 👉 Chat Display
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for speaker, message in st.session_state.history:
        if speaker == "user":
            avatar = "🧑"
            bubble_class = "user-bubble"
            alignment = "flex-end"
            avatar_position = "after"  # Avatar AFTER bubble for user
        else:
            avatar = "🤖"
            bubble_class = "bot-bubble"
            alignment = "flex-start"
            avatar_position = "before"  # Avatar BEFORE bubble for bot

        st.markdown(f'''
            <div style="display: flex; justify-content: {alignment}; margin-top: 10px;">
                <div style="display: flex; align-items: flex-start; gap: 8px;">
                    {'<div style="font-size:24px;">' + avatar + '</div>' if avatar_position == "before" else ''}
                    <div class="{bubble_class}">
                        <strong>{'You' if speaker == 'user' else 'WiseBuddy'}:</strong><br>{message}
                    </div>
                    {'<div style="font-size:24px;">' + avatar + '</div>' if avatar_position == "after" else ''}
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 👉 User Input
user_input = st.chat_input("💭 Type your message here:")

# 👉 Generate Response
if user_input:
    st.session_state.history.append(("user", user_input))
    
    # Get last bot response for context (if exists)
    prev_context = ""
    if len(st.session_state.history) > 1:
        # Search backwards through history for last bot message
        for msg in reversed(st.session_state.history[:-1]):
            if msg[0] == "bot":
                prev_context = msg[1]
                break
    
    prompt = f"""
    You are WiseBuddy, a friendly advice chatbot specializing in {st.session_state.current_category}. 
    {f"The previous conversation context was: '{prev_context}'" if prev_context else "This is a new conversation."}
    
    Respond kindly to: {user_input}
    """
    
    with st.spinner("🤖 WiseBuddy is typing..."):
        response = st.session_state.chat.send_message(prompt)
        bot_response = response.text
        st.session_state.history.append(("bot", bot_response))
    
    st.rerun()
