import streamlit as st 
import random 
import requests 
import google.generativeai as genai 
from huggingface_hub 
import InferenceClient

Load API keys from Streamlit secrets

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"] 
DEEPINFRA_API_KEY = st.secrets["DEEPINFRA_API_KEY"] 
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"] 
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

Configure Google Gemini

genai.configure(api_key=GOOGLE_API_KEY)

Configure Hugging Face

hf_client = InferenceClient(HUGGINGFACE_API_KEY)

st.set_page_config(page_title="WiseBuddy Chat", page_icon="💬") st.title("💬 WiseBuddy Chat") st.write("Chat with WiseBuddy about anything—life, goals, or just venting.")

Fallback advice messages

fallback_responses = [ "🌱 Every big journey starts with a single small step.", "✨ Keep going—you’re stronger than you think.", "💡 Take one action, however small, today.", "🔥 WiseBuddy believes in you. Every setback is a setup for a comeback!" ]

Session state for chat history

if 'messages' not in st.session_state: st.session_state['messages'] = []

Function to get AI response or fallback

def get_response(prompt): # Try Google Gemini try: model = genai.GenerativeModel('gemini-1.5-flash') response = model.generate_content(prompt) return response.text except: pass

# Try DeepInfra
try:
    headers = {"Authorization": f"Bearer {DEEPINFRA_API_KEY}"}
    json_data = {"inputs": prompt, "parameters": {"max_new_tokens": 150}}
    response = requests.post("https://api.deepinfra.com/v1/inference/meta-llama/Llama-3-8b-chat", headers=headers, json=json_data)
    if response.ok:
        return response.json().get('generated_text', 'No generated text.')
except:
    pass

# Try OpenRouter
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

# Try Hugging Face
try:
    response = hf_client.text_generation(prompt, max_new_tokens=150)
    return response
except:
    pass

# Fallback message
return random.choice(fallback_responses)

Input box

user_input = st.chat_input("Say something...") if user_input: st.session_state.messages.append({"role": "user", "content": user_input}) reply = get_response(user_input) st.session_state.messages.append({"role": "assistant", "content": reply})

Display chat history

for message in st.session_state.messages: with st.chat_message(message["role"]): st.markdown(message["content"])

