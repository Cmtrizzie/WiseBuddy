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

# Custom CSS for readability and chat bubbles
st.markdown("""
    <style>
    .chat-bubble {
        background-color: #f1f1f1;
        color: #333;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        word-wrap: break-word;
    }
    .user-bubble {
        background-color: #d1e7dd;
        color: #000;
        text-align: left;
    }
    .bot-bubble {
        background-color: #fff3cd;
        color: #000;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 WiseBuddy Chat")
st.write("Chat about anything—life, goals, or just venting.")

# Fallback advice messages
fallback_responses = [
    "🌱 Every big journey starts with a single small step.",
    "✨ Keep going—you’re stronger than you think.",
    "💡 Take one action, however small, today.",
    "🔥 WiseBuddy believes in you. Every setback is a setup for a comeback!"
]

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

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

# Input and response handling
user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble bot-bubble">{message["content"]}</div>', unsafe_allow_html=True)

# End of Step 1
