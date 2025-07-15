import streamlit as st
import uuid

# -------------- PAGE CONFIG -------------- #
st.set_page_config(
    page_title="My Assistant 🤖", layout="wide", initial_sidebar_state="expanded"
)

# -------------- SESSION STATE INIT -------------- #
if "topics" not in st.session_state:
    st.session_state.topics = {}
    st.session_state.active_topic = None
    st.session_state.active_mode = "Research"

# -------------- FUNCTIONAL HELPERS -------------- #
def create_topic(name):
    topic_id = str(uuid.uuid4())
    st.session_state.topics[topic_id] = {
        "name": name,
        "files": [],
        "summaries": {},
        "chat": [],
    }
    st.session_state.active_topic = topic_id

def switch_topic(topic_id):
    st.session_state.active_topic = topic_id

def set_mode(mode):
    st.session_state.active_mode = mode

# -------------- SIDEBAR: TOPICS & NAV -------------- #
with st.sidebar:
    st.title("📁 Topics")
    for tid, topic in st.session_state.topics.items():
        label = topic["name"] + (" ✅" if tid == st.session_state.active_topic else "")
        if st.button(label, key=f"switch_{tid}"):
            switch_topic(tid)

    st.markdown("---")
    new_topic = st.text_input("New Topic Name", key="new_topic")
    if st.button("➕ Create Topic") and new_topic:
        create_topic(new_topic)

# -------------- HEADER NAVIGATION -------------- #
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

with col1:
    st.markdown("### ☰")  # placeholder for future sidebar toggle
with col2:
    if st.button("📚 Research"):
        set_mode("Research")
with col3:
    if st.button("🛠️ Tools"):
        set_mode("Tools")
with col4:
    uploaded_files = st.file_uploader("Upload PDF(s)", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files and st.session_state.active_topic:
        st.session_state.topics[st.session_state.active_topic]["files"].extend(uploaded_files)

# -------------- MAIN PANEL -------------- #
if not st.session_state.active_topic:
    st.info("👈 Please create or select a topic to begin.")
    st.stop()

active_topic = st.session_state.topics[st.session_state.active_topic]
st.markdown(f"## 🧠 My Assistant – {active_topic['name']} ({st.session_state.active_mode})")

# PDF list
if active_topic["files"]:
    st.subheader("📄 Uploaded Files")
    for i, f in enumerate(active_topic["files"]):
        st.markdown(f"- `{f.name}`")
else:
    st.warning("No PDFs uploaded yet. Upload to begin working.")

# Active mode
if st.session_state.active_mode == "Research":
    st.subheader("🧠 Research Mode")
    st.write("(Summary + Ask AI features coming next phase...)")

elif st.session_state.active_mode == "Tools":
    st.subheader("🛠️ PDF Tools")
    st.write("(Merge, Split, Compress tools UI coming next phase...)")

# Footer
st.markdown("---")
st.caption("My Assistant v1.0 • Created with 💙 by you & Maya")
