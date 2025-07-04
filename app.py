# WiseBuddy: Auto-Switch Multi-API Chatbot (Streamlit)

import streamlit as st import google.generativeai as genai from huggingface_hub import InferenceClient import requests

=========================

API KEYS (From Streamlit Secrets)

=========================

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"] DEEPINFRA_API_KEY = st.secrets["DEEPINFRA_API_KEY"] OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"] HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

=========================

Initialize Clients

=========================

genai.configure(api_key=GOOGLE_API_KEY) hf_client = InferenceClient(token=HUGGINGFACE_API_KEY, model="meta-llama/Llama-3-8B-Instruct")

=========================

Streamlit Page Setup

=========================

st.set_page_config(page_title="WiseBuddy", layout="centered")

if 'chat_history' not in st.session_state: st.session_state.chat_history = []

st.title("WiseBuddy Chat 🤖") st.write("Chat about anything—life, goals, or just venting.")

col1, col2 = st.columns([5,1]) with col1: user_input = st.text_input("Type your message...", key="input_text", label_visibility="collapsed") with col2: send_clicked = st.button("Send")

=========================

Auto-Switching Logic

=========================

def get_response(prompt):

# 1. Google Gemini
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text
except:
    pass

# 2. DeepInfra
try:
    headers = {"Authorization": f"Bearer {DEEPINFRA_API_KEY}"}
    json_data = {"inputs": prompt, "parameters": {"max_new_tokens": 150}}
    response = requests.post("https://api.deepinfra.com/v1/inference/meta-llama/Llama-3-8b-chat", headers=headers, json=json_data)
    if response.ok and 'generated_text' in response.json():
        return response.json().get('generated_text')
except:
    pass

# 3. OpenRouter
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
    if response.ok and 'choices' in response.json():
        return response.json()['choices'][0]['message']['content']
except:
    pass

# 4. Hugging Face
try:
    response = hf_client.text_generation(prompt, max_new_tokens=150)
    return response
except:
    return "Sorry, all AI providers are currently unavailable. Please try again later."

=========================

Handle Send Button

=========================

if send_clicked and user_input: prompt = f"You are WiseBuddy, a friendly AI advisor. Respond to: {user_input}"

with st.spinner("WiseBuddy is thinking..."):
    reply = get_response(prompt)

st.session_state.chat_history.append(("You", user_input))
st.session_state.chat_history.append(("WiseBuddy", reply))
st.experimental_rerun()

=========================

Display Chat History

=========================

st.markdown("""

<div style='max-height:500px; overflow-y: auto; padding:10px; border:1px solid #ddd; border-radius:10px; background-color:#fff;'>
""", unsafe_allow_html=True)for speaker, message in st.session_state.chat_history: st.markdown(f""" <div style='background-color:#f9f9f9; padding:10px; margin-bottom:10px; border-radius:8px;'> <strong>{speaker}:</strong><br>{message} </div> """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

