# app.py
import streamlit as st
import sqlite3
import datetime
import os
import shutil
from agent import run_agent
from logging_config import setup_logging

setup_logging()

DB_NAME = "chat_history.db"


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
    """Return messages in chronological order (oldest first)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT timestamp, role, content FROM messages ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_messages_desc():
    """Return messages in reverse chronological order (newest first)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT timestamp, role, content FROM messages ORDER BY id DESC")
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


def get_latest_chat_pair():
    """Return the most recent user + assistant messages as a list."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT 2")
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))


def clear_all_messages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages")
    conn.commit()
    conn.close()


# Initialize database
init_db()


# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Online Store AI Assistant", layout="wide")

st.title("🛒 Online Store AI Assistant")
st.write("Ask me about orders, products, or alternatives.")


# ----------------------------
# Sidebar – Full Chat History (grouped by exchange, latest first)
# ----------------------------
with st.sidebar:
    st.header("📜 Chat History")

    if st.button("🗑 Clear All Chats"):
        clear_all_messages()
        if "last_response" in st.session_state:
            del st.session_state["last_response"]
        st.rerun()

    # Get messages in chronological order
    chrono_msgs = get_all_messages_chrono()

    if chrono_msgs:
        # Group into exchanges: (user_message, assistant_message)
        # We assume messages alternate: user, assistant, user, assistant, ...
        pairs = []
        for i in range(0, len(chrono_msgs), 2):
            user_msg = chrono_msgs[i]
            assistant_msg = chrono_msgs[i + 1] if i + 1 < len(chrono_msgs) else None
            pairs.append((user_msg, assistant_msg))

        # Display pairs in reverse order (latest exchange first)
        for user_msg, assistant_msg in reversed(pairs):
            # Display user message
            if user_msg:
                ts, role, content = user_msg
                try:
                    time_str = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                except:
                    time_str = ""
                st.markdown(
                    f"""
**You ({time_str})**  

{content}

"""
                )

            # Display assistant message
            if assistant_msg:
                ts, role, content = assistant_msg
                try:
                    time_str = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                except:
                    time_str = ""
                st.markdown(
                    f"""
**Assistant ({time_str})**  

{content}

---
"""
                )
            else:
                # If no assistant message (should not happen), add a separator
                st.markdown("---")

        st.caption(f"Total messages: {len(chrono_msgs)}")
    else:
        st.info("No conversations yet.")


# ----------------------------
# Input Form (with processing flag)
# ----------------------------
if "processing" not in st.session_state:
    st.session_state.processing = False

with st.form(key="chat_form", clear_on_submit=True):
    user_question = st.text_input(
        "Your question:",
        placeholder="Ask Question eg. track my orderid",
        disabled=st.session_state.processing
    )
    submit_button = st.form_submit_button(
        "Ask",
        disabled=st.session_state.processing
    )


# ----------------------------
# Process the user question
# ----------------------------
if submit_button and user_question and not st.session_state.processing:
    st.session_state.processing = True

    # Save user message
    save_message("user", user_question)

    # Get assistant response
    with st.spinner("Thinking..."):
        response = run_agent(user_question)

    # Avoid duplicates
    last_assistant = get_last_assistant_message()
    if response != last_assistant:
        save_message("assistant", response)

    # Store latest response for immediate display (optional)
    st.session_state.last_response = response

    st.session_state.processing = False
    st.rerun()

st.divider()

# ----------------------------
# Main Chat – Latest Conversation Pair
# ----------------------------
st.subheader("💬 Latest Conversation")

latest_pair = get_latest_chat_pair()
if latest_pair:
    for role, content in latest_pair:
        if role == "user":
            st.markdown(f"### 🧑 You\n{content}")
        else:
            st.markdown(f"### 🤖 Assistant\n{content}")
else:
    st.info("No messages yet.")
