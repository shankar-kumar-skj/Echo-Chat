# app.py
import streamlit as st
import sqlite3
import datetime
import os
import shutil
from agent import run_agent
from logging_config import setup_logging
from advanced_features import process_with_advanced_features

setup_logging()

DB_NAME = "chat_history.db"

# ----------------------------
# Custom CSS for left-right chat bubbles
# ----------------------------
st.markdown("""
<style>
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
        margin-bottom: 0.3rem;
    }
    .user-message {
        align-self: flex-end;
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 1rem 1rem 0 1rem;
        max-width: 80%;
        word-wrap: break-word;
        font-size: 0.95rem;
    }
    .assistant-message {
        align-self: flex-start;
        background-color: #f1f1f1;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 1rem 1rem 1rem 0;
        max-width: 80%;
        word-wrap: break-word;
        font-size: 0.95rem;
    }
    .timestamp {
        font-size: 0.65rem;
        opacity: 0;
        transition: opacity 0.2s;
        margin-top: 0.1rem;
    }
    .chat-container:hover .timestamp {
        opacity: 0.6;
    }
    .user-message .timestamp {
        color: rgba(255,255,255,0.7);
        text-align: right;
    }
    .assistant-message .timestamp {
        color: rgba(0,0,0,0.5);
        text-align: left;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.25rem 1rem;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }
    .stTextInput > label {
        display: none;
    }
    .sidebar-pair {
        border-bottom: 1px solid #eee;
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Database Functions
# ----------------------------
def is_valid_sqlite_db(db_path):
    if not os.path.exists(db_path):
        return False
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        return True
    except sqlite3.DatabaseError:
        return False
    finally:
        if conn:
            conn.close()

def init_db():
    if not is_valid_sqlite_db(DB_NAME):
        if os.path.exists(DB_NAME):
            backup_name = DB_NAME + ".bak"
            try:
                shutil.move(DB_NAME, backup_name)
                print(f"⚠️ Corrupted database moved to {backup_name}")
            except Exception:
                try:
                    os.remove(DB_NAME)
                except:
                    pass

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT,
                content TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("✅ New database created.")
    else:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT,
                content TEXT
            )
        """)
        conn.commit()
        conn.close()

def save_message(role, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def get_all_messages_chrono():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT timestamp, role, content FROM messages ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_last_assistant_message():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM messages WHERE role='assistant' ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def clear_all_messages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

init_db()

# ----------------------------
# Streamlit App
# ----------------------------
st.set_page_config(page_title="Online Store AI Assistant", layout="wide")

st.title("🛒 Online Store AI Assistant")
st.write("Ask me about orders, products, or alternatives.")

# Sidebar – Full Chat History (grouped by pairs, latest first)
with st.sidebar:
    st.header("📜 Chat History")
    if st.button("🗑 Clear All Chats"):
        clear_all_messages()
        st.rerun()

    chrono = get_all_messages_chrono()
    if chrono:
        pairs = []
        i = 0
        while i < len(chrono):
            user_row = chrono[i]
            if user_row[1] == "user":
                assistant_row = chrono[i+1] if i+1 < len(chrono) and chrono[i+1][1] == "assistant" else None
                pairs.append((user_row, assistant_row))
                i += 2 if assistant_row else 1
            else:
                i += 1
        if not pairs:
            st.info("No complete conversations yet.")
        else:
            for user_msg, assistant_msg in reversed(pairs):
                if user_msg:
                    ts, role, content = user_msg
                    try:
                        time_str = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                    except:
                        time_str = ""
                    st.markdown(f"**You ({time_str})**  \n\n{content}\n")
                if assistant_msg:
                    ts, role, content = assistant_msg
                    try:
                        time_str = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                    except:
                        time_str = ""
                    st.markdown(f"**Assistant ({time_str})**  \n\n{content}\n---")
            st.caption(f"Total messages: {len(chrono)}")
    else:
        st.info("No conversations yet.")

# Main Chat Area – Display all messages in left/right bubbles
st.subheader("💬 Conversation")

all_msgs = get_all_messages_chrono()
if all_msgs:
    for ts, role, content in all_msgs:
        try:
            time_str = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        except:
            time_str = ""
        if role == "user":
            st.markdown(
                f"""
                <div class="chat-container">
                    <div class="user-message">
                        {content}
                        <div class="timestamp">{time_str}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="chat-container">
                    <div class="assistant-message">
                        {content}
                        <div class="timestamp">{time_str}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("No messages yet. Start a conversation below.")

st.divider()

# Input Form with ">" button
if "processing" not in st.session_state:
    st.session_state.processing = False

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_question = st.text_input(
            "Your question:",
            placeholder="e.g., track order ORD-1002, compare products in ORD-1002, search for shoes",
            disabled=st.session_state.processing,
            label_visibility="collapsed"
        )
    with col2:
        submit_button = st.form_submit_button(">", disabled=st.session_state.processing)

if submit_button and user_question and not st.session_state.processing:
    st.session_state.processing = True

    save_message("user", user_question)

    with st.spinner("Thinking..."):
        response = process_with_advanced_features(user_question, agent_func=run_agent)

    last_assistant = get_last_assistant_message()
    if response != last_assistant:
        save_message("assistant", response)

    st.session_state.processing = False
    st.rerun()