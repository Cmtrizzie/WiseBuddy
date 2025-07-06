import streamlit as st from streamlit.components.v1 import html

Configure Streamlit page

st.set_page_config( page_title="WiseBuddy Chatbot", layout="wide", initial_sidebar_state="collapsed" )

Hide Streamlit default elements

hide_streamlit_style = """

<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>""" st.markdown(hide_streamlit_style, unsafe_allow_html=True)

Full WiseBuddy Chatbot Interface

wisebuddy_html = r"""

<!DOCTYPE html><html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>WiseBuddy Chatbot</title>
<script src='https://cdn.tailwindcss.com'></script>
<style>
body { font-family: Arial, sans-serif; background-color: #f3f4f6; margin: 0; }
.container { max-width: 400px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); background: #fff; border-radius: 10px; overflow: hidden; }
.header { background-color: #4f46e5; color: white; padding: 20px; text-align: center; font-size: 1.25rem; font-weight: bold; }
.chatbox { padding: 20px; height: 400px; overflow-y: auto; background: #f9fafb; }
.chat-message { margin-bottom: 10px; padding: 10px; border-radius: 8px; max-width: 80%; }
.bot { background-color: #e0e7ff; align-self: flex-start; }
.user { background-color: #d1fae5; align-self: flex-end; }
.input-area { display: flex; border-top: 1px solid #ddd; }
.input-area input { flex: 1; padding: 10px; border: none; border-radius: 0 0 0 10px; }
.input-area button { background: #4f46e5; color: white; border: none; padding: 0 20px; border-radius: 0 0 10px 0; cursor: pointer; }
</style>
</head>
<body>
<div class='container'>
  <div class='header'>WiseBuddy</div>
  <div class='chatbox' id='chatbox'>
    <div class='chat-message bot'>Hi there! I'm WiseBuddy. How can I help you today?</div>
  </div>
  <div class='input-area'>
    <input type='text' id='userInput' placeholder='Type your message...'>
    <button onclick='sendMessage()'>Send</button>
  </div>
</div>
<script>
function sendMessage() {
  const input = document.getElementById('userInput');
  const message = input.value.trim();
  if (message === '') return;const chatbox = document.getElementById('chatbox');

const userDiv = document.createElement('div'); userDiv.className = 'chat-message user'; userDiv.innerText = message; chatbox.appendChild(userDiv);

input.value = ''; chatbox.scrollTop = chatbox.scrollHeight;

setTimeout(() => { const botDiv = document.createElement('div'); botDiv.className = 'chat-message bot'; botDiv.innerText = generateBotResponse(message); chatbox.appendChild(botDiv); chatbox.scrollTop = chatbox.scrollHeight; }, 1000); }

function generateBotResponse(message) { const responses = [ "That's interesting! Tell me more.", "I'm here to help. What else can I do for you?", "Let's explore that idea together!", "I'm not sure I understand, could you elaborate?" ]; return responses[Math.floor(Math.random() * responses.length)]; } </script>

</body>
</html>
"""Display in Streamlit

html(wisebuddy_html, height=700, scrolling=True)

