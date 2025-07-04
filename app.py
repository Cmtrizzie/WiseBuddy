import streamlit as st
import google.generativeai as genai
import random

# 👉 Configure your Gemini API Key
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")
model = genai.GenerativeModel('gemini-1.5-flash')

# 👉 Streamlit Page Setup
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# 👉 CSS Styling (Background, bubbles, avatars, title glow)
st.markdown("""
    <style>
    body {
        background-color: #f7f9fc;
    }

    .big-font {
        font-size: 26px !important;
        font-weight: bold;
        color: #2c3e50;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 10px;
    }

    .user-bubble {
        background-color: #d0f0c0;  /* Mint Green */
        padding: 14px 18px;
        border-radius: 25px;
        max-width: 70%;
        font-size: 16px;
        margin-left: auto;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        color: #333;
    }

    .bot-bubble {
        background-color: #e0d4f7;  /* Lavender */
        padding: 14px 18px;
        border-radius: 25px;
        max-width: 70%;
        font-size: 16px;
        margin-right: auto;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        color: #333;
    }

    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: white;
    }

    .user-avatar { background-color: #4CAF50; }  /* Green circle */
    .bot-avatar { background-color: #6c63ff; }   /* Purple circle */
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

# 👉 Clear Chat Button
if st.button("🗑️ Clear Chat"):
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.history = []
    st.session_state.current_category = category

# 👉 Start Chat if None
if st.session_state.chat is None:
    st.session_state.chat = model.start_chat(history=[])

# 👉 Display Chat History
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for speaker, message in st.session_state.history:
        if speaker == "user":
            avatar = '<div class="avatar user-avatar">🧑</div>'
            bubble_class = "user-bubble"
            alignment = "flex-end"
        else:
            avatar = '<div class="avatar bot-avatar">🤖</div>'
            bubble_class = "bot-bubble"
            alignment = "flex-start"

        st.markdown(f'''
            <div style="display: flex; justify-content: {alignment}; margin-top: 10px;">
                <div style="display: flex; align-items: flex-start; gap: 8px;">
                    {' ' + avatar if speaker != 'user' else ''}
                    <div class="{bubble_class}">
                        <strong>{'You' if speaker == 'user' else 'WiseBuddy'}:</strong><br>{message}
                    </div>
                    {' ' + avatar if speaker == 'user' else ''}
                </div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# 👉 User Input
user_input = st.chat_input("💭 Type your message here:")

# 👉 Generate WiseBuddy Response
if user_input:
    st.session_state.history.append(("user", user_input))
    prompt = f"""
    You are WiseBuddy, a friendly advice chatbot specializing in {st.session_state.current_category}. 
    The user has been chatting about: {st.session_state.history[-2][1] if len(st.session_state.history) > 1 else 'new conversation'}
    
    Respond kindly to: {user_input}
    """

    with st.spinner("🤖 WiseBuddy is typing..."):
        response = st.session_state.chat.send_message(prompt)
        bot_response = response.text
        st.session_state.history.append(("bot", bot_response))

    st.rerun()
