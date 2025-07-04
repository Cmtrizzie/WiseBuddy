import streamlit as st
import google.generativeai as genai

# Configure your actual Gemini API key
genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")

model = genai.GenerativeModel('gemini-1.5-flash')

# Page configuration
st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖", layout="centered")

# Custom styling
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    .chat-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        color: #333333;
        font-size: 17px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title
st.markdown('<h1 style="text-align: center;">💬 WiseBuddy Chat 🧠</h1>', unsafe_allow_html=True)
st.write("Talk to WiseBuddy like a real conversation. Your friendly AI is here to listen and help.")

# Advice category
category = st.selectbox("📝 Choose your advice style:", [
    "🌟 Motivation & Positivity",
    "💡 Business & Wealth",
    "❤️ Love & Relationships",
    "🧘 Mindfulness & Peace"
])

# User Input
user_input = st.text_input("💭 Say something to WiseBuddy:")

if st.button("Send") and user_input:
    with st.spinner("WiseBuddy is thinking..."):
        prompt = f"You are WiseBuddy, a kind chatbot. Give friendly, helpful advice for: {user_input} (Topic: {category})"
        response = model.generate_content(prompt)
        reply = response.text

        # Save to chat history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("WiseBuddy", reply))

# Display chat history
for sender, message in st.session_state.chat_history:
    st.markdown(f'<div class="chat-box"><strong>{sender}:</strong><br>{message}</div>', unsafe_allow_html=True)
