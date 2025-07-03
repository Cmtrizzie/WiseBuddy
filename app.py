import streamlit as st
import google.generativeai as genai

genai.configure(api_key="AIzaSyCCrH9lwWQcH38Vbv287H-CTPXaR5U_lF4")  # 👉 Replace with your key inside quotes

model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="WiseBuddy 🧠", page_icon="🤖")
st.title("💬 WiseBuddy")
st.subheader("Your Friendly AI Advice Bot")

st.markdown("""
Talk to **WiseBuddy** about anything—stress, goals, or just life. Type below and get AI-powered advice.
""")

user_input = st.text_input("💭 What's on your mind?")

if user_input:
    with st.spinner("WiseBuddy is thinking..."):
        response = model.generate_content(
            f"You are WiseBuddy, a friendly advice bot. Give helpful advice for this: {user_input}"
        )
        st.success("Here’s WiseBuddy’s advice:")
        st.write(response.text)
