import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Complaint Management", layout="centered")

DB_PATH = os.path.join(os.getcwd(), "complaints.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

# ---- DB Setup ----
conn = get_connection()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    category TEXT,
    description TEXT,
    status TEXT
)
""")
conn.commit()
conn.close()

# ---- Session State ----
if "role" not in st.session_state:
    st.session_state.role = None

# ---- LOGIN PAGE ----
def login_page():
    st.title("🔐 Login")

    role = st.selectbox("Login as", ["Student", "Admin"])

    if role == "Student":
        name = st.text_input("Student Name")
        if st.button("Login"):
            if name.strip():
                st.session_state.role = "student"
                st.session_state.user = name
                st.rerun()
            else:
                st.error("Please enter your name")

    else:  # Admin
        username = st.text_input("Admin Username")
        password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("Invalid admin credentials")

# ---- STUDENT PAGE ----
def student_page():
    st.title("🎓 Student Complaint Portal")
    st.write(f"Welcome, **{st.session_state.user}**")

    category = st.selectbox("Category", ["Hostel", "Lab", "Administration"])
    description = st.text_area("Complaint Description")

    if st.button("Submit Complaint"):
        if description.strip():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO complaints (student_name, category, description, status) VALUES (?,?,?,?)",
                (st.session_state.user, category, description, "Pending")
            )
            conn.commit()
            conn.close()
            st.success("✅ Complaint submitted successfully")
        else:
            st.error("Please enter complaint details")

    if st.button("Logout"):
        st.session_state.role = None
        st.rerun()

# ---- ADMIN PAGE ----
def admin_page():
    st.title("🛠️ Admin Dashboard")

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM complaints", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)

    st.subheader("Update Complaint Status")
    cid = st.number_input("Complaint ID", min_value=1, step=1)
    status = st.selectbox("New Status", ["Pending", "Resolved"])

    if st.button("Update Status"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE complaints SET status=? WHERE id=?",
            (status, cid)
        )
        conn.commit()
        conn.close()
        st.success("✅ Status updated")

    if st.button("Logout"):
        st.session_state.role = None
        st.rerun()

# ---- ROUTING ----
if st.session_state.role is None:
    login_page()
elif st.session_state.role == "student":
    student_page()
elif st.session_state.role == "admin":
    admin_page()
