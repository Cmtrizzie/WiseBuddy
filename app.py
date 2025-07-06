import streamlit as st
import time
import uuid
from datetime import datetime
import json
import base64

# Initialization
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = [
        {'id': 'chat-1', 'title': 'Conversation with John Doe', 'icon': 'comments', 'messages': []},
        {'id': 'chat-2', 'title': 'Discussion about AI Ethics', 'icon': 'robot', 'messages': []},
        {'id': 'chat-3', 'title': 'Summary of Project X', 'icon': 'file-alt', 'messages': []},
    ]

if 'current_chat' not in st.session_state:
    st.session_state.current_chat = st.session_state.chat_sessions[0]['id']

if 'sidebar_open' not in st.session_state:
    st.session_state.sidebar_open = True

if 'editing_chat' not in st.session_state:
    st.session_state.editing_chat = None

if 'deleting_chat' not in st.session_state:
    st.session_state.deleting_chat = None

if 'menu_open' not in st.session_state:
    st.session_state.menu_open = False

# CSS Styles
def inject_css():
    st.markdown("""
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5;
        }

        .chatbot-messages::-webkit-scrollbar {
            width: 8px;
        }

        .chatbot-messages::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .chatbot-messages::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 10px;
        }

        .chatbot-messages::-webkit-scrollbar-thumb:hover {
            background: #bbb;
        }

        @keyframes bounce {
            0%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-8px); }
        }

        .typing-indicator .dot {
            animation: bounce 1.4s infinite ease-in-out;
        }

        .typing-indicator .dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-indicator .dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        .dropdown-menu {
            position: absolute;
            top: 100%;
            right: 0;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            min-width: 150px;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transform: translateY(-10px);
            transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s ease;
        }

        .dropdown-menu.active {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .dropdown-menu ul {
            list-style: none;
            padding: 8px 0;
            margin: 0;
        }

        .dropdown-menu ul li {
            padding: 10px 15px;
            cursor: pointer;
            color: #333;
            font-size: 0.95em;
            transition: background-color 0.2s ease;
        }

        .dropdown-menu ul li:hover {
            background-color: #f0f2f5;
        }

        .main-app-container {
            display: flex;
            height: 100vh;
            width: 100%;
            max-width: 900px;
            background-color: #f0f2f5;
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        .sidebar-container {
            width: 250px;
            background-color: #3f5e82;
            color: #ffffff;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            height: 100%;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
        }

        .sidebar-header {
            padding: 15px 20px;
            font-size: 1.2em;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .sidebar-close-btn {
            font-size: 1.5em;
            cursor: pointer;
            opacity: 0.8;
            transition: opacity 0.2s ease;
        }

        .sidebar-close-btn:hover {
            opacity: 1;
        }

        .sidebar-history {
            flex-grow: 1;
            overflow-y: auto;
            padding: 15px 10px;
        }

        .sidebar-history ul {
            list-style-type: none !important; /* Force remove bullets */
            padding: 0 !important; /* Remove default padding for list items */
            margin: 0;
        }

        .sidebar-history ul li {
            padding: 14px 15px;
            margin-bottom: 15px; /* Increased spacing */
            cursor: pointer;
            transition: background-color 0.2s ease;
            font-size: 0.95em;
            display: flex;
            align-items: center;
            justify-content: flex-start; /* Align items to the start */
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px; /* Slightly more rounded */
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .sidebar-history ul li:last-child {
            margin-bottom: 0;
        }

        .sidebar-history ul li:hover {
            background-color: rgba(255, 255, 255, 0.15);
        }

        .sidebar-history ul li.active {
            background-color: rgba(255, 255, 255, 0.25);
            font-weight: bold;
            border-color: rgba(255, 255, 255, 0.3);
        }

        .sidebar-history ul li .chat-title {
            flex-grow: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar-history ul li .rename-input {
            background-color: rgba(255, 255, 255, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 5px;
            padding: 5px 8px;
            font-size: 0.9em;
            color: #fff;
            outline: none;
            width: calc(100% - 10px);
        }

        .chatbot-container {
            flex-grow: 1;
            background-color: white;
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
        }

        .chatbot-header {
            background-color: #5a7d9a;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .avatar {
            width: 40px;
            height: 40px;
            background-color: #8cabc2;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            font-size: 18px;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .header-right {
            position: relative;
        }

        .menu-icon {
            font-size: 20px;
            cursor: pointer;
            opacity: 0.8;
            transition: opacity 0.2s;
        }

        .menu-icon:hover {
            opacity: 1;
        }

        .chatbot-messages {
            flex-grow: 1;
            overflow-y: auto;
            padding: 20px;
            background-color: #fdfdfd;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message-bubble {
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
        }

        .bot-message {
            background-color: #e0e7ee;
            color: #333;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        .user-message {
            background-color: #a3c2e0;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .quick-replies {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }

        .quick-reply-btn {
            background-color: #d1e2f3;
            color: #3f5e82;
            border: 1px solid #b3d1ed;
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }

        .quick-reply-btn:hover {
            background-color: #c0d7ee;
            transform: translateY(-1px);
        }

        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
            background-color: #e0e7ee;
            border-radius: 18px;
            padding: 12px 16px;
            width: fit-content;
            margin-top: 12px;
            border-bottom-left-radius: 4px;
        }

        .dot {
            width: 8px;
            height: 8px;
            background-color: #8cabc2;
            border-radius: 50%;
        }

        .chatbot-input-area {
            padding: 15px;
            background-color: #f7f9fb;
            border-top: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .chatbot-input-area input {
            flex-grow: 1;
            padding: 12px 18px;
            border: 1px solid #ddd;
            border-radius: 24px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        .chatbot-input-area input:focus {
            border-color: #5a7d9a;
            box-shadow: 0 0 0 3px rgba(90, 125, 154, 0.2);
        }

        .send-button {
            background-color: #5a7d9a;
            color: white;
            border: none;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .send-button:hover {
            background-color: #4a6c8a;
            transform: translateY(-2px);
        }

        .send-button:active {
            transform: translateY(0);
        }

        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1001;
        }

        .modal-content {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
            max-width: 350px;
            width: 90%;
            text-align: center;
        }

        .modal-content h4 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.2em;
            color: #333;
        }

        .modal-content p {
            margin-bottom: 25px;
            color: #555;
            line-height: 1.5;
        }

        .modal-buttons {
            display: flex;
            justify-content: space-around;
            gap: 15px;
        }

        .modal-btn {
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease, transform 0.1s ease;
            flex: 1;
        }

        .modal-btn.confirm-btn {
            background-color: #ef4444;
            color: #ffffff;
            border: none;
        }

        .modal-btn.confirm-btn:hover {
            background-color: #dc2626;
            transform: translateY(-1px);
        }

        .modal-btn.cancel-btn {
            background-color: #e5e7eb;
            color: #374151;
            border: none;
        }

        .modal-btn.cancel-btn:hover {
            background-color: #d1d5db;
            transform: translateY(-1px);
        }
        
        /* New styling for chat history items */
        .chat-history-item {
            display: flex;
            align-items: center;
            padding: 14px 15px;
            margin-bottom: 15px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.2s ease;
        }
        
        .chat-history-item:hover {
            background-color: rgba(255, 255, 255, 0.15);
        }
        
        .chat-history-item.active {
            background-color: rgba(255, 255, 255, 0.25);
            font-weight: bold;
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .chat-history-icon {
            margin-right: 10px;
            font-size: 14px;
            opacity: 0.8;
        }
        
        /* Responsive styles */
        @media (max-width: 768px) {
            .main-app-container {
                flex-direction: column;
                height: auto;
            }
            
            .sidebar-container {
                width: 100%;
                height: auto;
                max-height: 50vh;
                display: none;
            }
            
            .sidebar-container.open {
                display: flex;
            }
            
            .chatbot-container {
                width: 100%;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# Font Awesome icons
def font_awesome():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """, unsafe_allow_html=True)

# Helper functions
def get_current_chat():
    for chat in st.session_state.chat_sessions:
        if chat['id'] == st.session_state.current_chat:
            return chat
    return None

def add_message(chat_id, message, is_user=False):
    for chat in st.session_state.chat_sessions:
        if chat['id'] == chat_id:
            chat['messages'].append({
                'id': str(uuid.uuid4()),
                'text': message,
                'is_user': is_user,
                'timestamp': datetime.now().isoformat()
            })
            break

def new_chat_session():
    chat_id = f"chat-{len(st.session_state.chat_sessions)+1}"
    new_chat = {
        'id': chat_id,
        'title': f'New Chat {len(st.session_state.chat_sessions)+1}',
        'icon': 'comment',
        'messages': []
    }
    st.session_state.chat_sessions.append(new_chat)
    st.session_state.current_chat = chat_id
    st.session_state.editing_chat = None
    st.session_state.deleting_chat = None

def delete_chat(chat_id):
    if len(st.session_state.chat_sessions) <= 1:
        return
    st.session_state.chat_sessions = [chat for chat in st.session_state.chat_sessions if chat['id'] != chat_id]
    if st.session_state.current_chat == chat_id:
        st.session_state.current_chat = st.session_state.chat_sessions[0]['id']
    st.session_state.deleting_chat = None

def rename_chat(chat_id, new_title):
    for chat in st.session_state.chat_sessions:
        if chat['id'] == chat_id:
            chat['title'] = new_title
            break
    st.session_state.editing_chat = None

# Streamlit App
def main():
    st.set_page_config(
        page_title="WiseBuddy Chatbot",
        page_icon="💬",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    inject_css()
    font_awesome()
    
    # Main container
    st.markdown("""
    <div class="main-app-container">
        <!-- Sidebar Container -->
        <div class="sidebar-container">
            <div class="sidebar-header">
                <span>Chats</span>
            </div>
            <div class="sidebar-history" id="sidebar-history-list">
    """, unsafe_allow_html=True)
    
    # Render chat history
    for chat in st.session_state.chat_sessions:
        active_class = "active" if chat['id'] == st.session_state.current_chat else ""
        editing = st.session_state.editing_chat == chat['id']
        
        if editing:
            new_title = st.text_input(
                "Rename chat", 
                value=chat['title'], 
                key=f"rename_{chat['id']}",
                on_change=lambda cid=chat['id']: rename_chat(cid, st.session_state[f"rename_{cid}"])
            )
        else:
            if st.button(chat['title'], key=f"chat_{chat['id']}"):
                st.session_state.current_chat = chat['id']
            
            st.markdown(f"""
            <div class="chat-history-item {active_class}">
                <i class="fas fa-{chat['icon']} chat-history-icon"></i>
                <span class="chat-title">{chat['title']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            if col1.button("✏️ Rename", key=f"edit_{chat['id']}"):
                st.session_state.editing_chat = chat['id']
            if col2.button("🗑️ Delete", key=f"del_{chat['id']}"):
                st.session_state.deleting_chat = chat['id']
    
    st.markdown("""
            </div>
        </div>
        
        <!-- Chatbot Container -->
        <div class="chatbot-container">
            <!-- Chatbot Header -->
            <div class="chatbot-header">
                <div class="header-left">
                    <div class="avatar">WB</div>
                    <h3>WiseBuddy</h3>
                </div>
                <div class="header-right">
                    <i class="fas fa-ellipsis-v menu-icon"></i>
                </div>
            </div>
            
            <!-- Chat Messages Area -->
            <div class="chatbot-messages">
    """, unsafe_allow_html=True)
    
    # Display messages for current chat
    current_chat = get_current_chat()
    if current_chat:
        for msg in current_chat['messages']:
            if msg['is_user']:
                st.markdown(f"""
                <div class="message-bubble user-message">
                    <p class="m-0">{msg['text']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-bubble bot-message">
                    <p class="m-0">{msg['text']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("""
            </div>
            
            <!-- Chat Input Area -->
            <div class="chatbot-input-area">
                <i class="fas fa-microphone"></i>
                <input type="text" id="user-input" placeholder="Type your message...">
                <button class="send-button" id="send-button">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # New chat button
    if st.button("New Chat", use_container_width=True):
        new_chat_session()
        st.experimental_rerun()
    
    # User input
    user_input = st.text_input("Type your message", key="user_input", label_visibility="collapsed")
    
    # Send button functionality
    if st.button("Send", use_container_width=True) or user_input:
        if user_input:
            add_message(st.session_state.current_chat, user_input, is_user=True)
            
            # Simulate bot response
            with st.spinner(""):
                time.sleep(1.5)
                bot_response = "Thanks for your message! I'm still learning, but I'll get back to you soon."
                add_message(st.session_state.current_chat, bot_response, is_user=False)
            
            st.experimental_rerun()
    
    # Confirmation modal for delete
    if st.session_state.deleting_chat:
        st.markdown("""
        <div class="modal-overlay">
            <div class="modal-content">
                <h4>Confirm Deletion</h4>
                <p>Are you sure you want to delete this chat history? This action cannot be undone.</p>
                <div class="modal-buttons">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        if col1.button("Cancel", use_container_width=True):
            st.session_state.deleting_chat = None
            st.experimental_rerun()
        if col2.button("Delete", type="primary", use_container_width=True):
            delete_chat(st.session_state.deleting_chat)
            st.session_state.deleting_chat = None
            st.experimental_rerun()
        
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
