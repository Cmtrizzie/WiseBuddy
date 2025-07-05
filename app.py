import streamlit as st
import random
import requests
import google.generativeai as genai
from huggingface_hub import InferenceClient

# Load API keys from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
DEEPINFRA_API_KEY = st.secrets["DEEPINFRA_API_KEY"]
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

# Configure Google Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Configure Hugging Face
hf_client = InferenceClient(HUGGINGFACE_API_KEY)

# Set page config
st.set_page_config(page_title="WiseBuddy Chat", page_icon="💬", layout="wide")

if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False

st.sidebar.title("🌙 Settings")
st.session_state['dark_mode'] = st.sidebar.toggle("Enable Dark Mode", value=st.session_state['dark_mode'])

st.sidebar.title("📜 Chat History")
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if st.session_state['messages']:
    for i, msg in enumerate(st.session_state['messages']):
        role = "You" if msg['role'] == 'user' else "WiseBuddy"
        st.sidebar.markdown(f"**{role}:** {msg['content'][:50]}...")
else:
    st.sidebar.write("No chat history yet.")

background_color = "#1e1e1e" if st.session_state['dark_mode'] else "#ffffff"
text_color = "#e0e0e0" if st.session_state['dark_mode'] else "#000000"
user_bubble_color = "#3c3c3c" if st.session_state['dark_mode'] else "#d1e7dd"
bot_bubble_color = "#2a2a2a" if st.session_state['dark_mode'] else "#fff3cd"

st.markdown(f"""
    <style>
    .main {{
        background-color: {background_color};
        color: {text_color};
    }}
    .chat-bubble {{
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        word-wrap: break-word;
    }}
    .user-bubble {{
        background-color: {user_bubble_color};
        color: {text_color};
    }}
    .bot-bubble {{
        background-color: {bot_bubble_color};
        color: {text_color};
    }}
    .chat-input-container {{
        display: flex;
        align-items: center;
        width: 100%;
        margin-top: 10px;
    }}
    .chat-input-field {{
        flex: 1;
        padding: 10px;
        border-radius: 5px;
        border: none;
        margin-right: 5px;
    }}
    .chat-button {{
        padding: 10px 15px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("💬 WiseBuddy Chat")
st.write("Chat about anything—life, goals, or just venting.")

fallback_responses = [
    "🌱 Every big journey starts with a single small step.",
    "✨ Keep going—you’re stronger than you think.",
    "💡 Take one action, however small, today.",
    "🔥 WiseBuddy believes in you. Every setback is a setup for a comeback!"
]

# AI response function
def get_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except:
        pass

    try:
        headers = {"Authorization": f"Bearer {DEEPINFRA_API_KEY}"}
        json_data = {"inputs": prompt, "parameters": {"max_new_tokens": 150}}
        response = requests.post("https://api.deepinfra.com/v1/inference/meta-llama/Llama-3-8b-chat", headers=headers, json=json_data)
        if response.ok:
            return response.json().get('generated_text', 'No generated text.')
    except:
        pass

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        json_data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json_data)
        if response.ok:
            return response.json()['choices'][0]['message']['content']
    except:
        pass

    try:
        response = hf_client.text_generation(prompt, max_new_tokens=150)
        return response
    except:
        pass

    return random.choice(fallback_responses)

user_input = st.chat_input("Type a message or click mic 🎤")
if user_input:
    st.session_state['messages'].append({"role": "user", "content": user_input})
    reply = get_response(user_input)
    st.session_state['messages'].append({"role": "assistant", "content": reply})

st.markdown("<script>window.scrollTo(0,document.body.scrollHeight);</script>", unsafe_allow_html=True)

for message in st.session_state['messages']:
    role_class = "user-bubble" if message["role"] == "user" else "bot-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)
