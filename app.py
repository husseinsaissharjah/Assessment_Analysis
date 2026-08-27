import streamlit as st
import sqlite3
import hashlib
import secrets

DB = "sais.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT,
        role TEXT NOT NULL,
        password_hash TEXT NOT NULL
    )''')
    # Default admin (only first time)
    cur = c.execute("SELECT COUNT(*) FROM users WHERE username=?", ("admin",))
    if cur.fetchone()[0] == 0:
        pwd = "admin123"
        h = hashlib.sha256(pwd.encode()).hexdigest()
        c.execute("INSERT INTO users (username, name, role, password_hash) VALUES (?,?,?,?)",
                  ("admin", "Administrator", "admin", h))
    conn.commit()
    conn.close()

def check_login(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    cur = c.execute("SELECT id, name, role, password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and row[3] == hashlib.sha256(password.encode()).hexdigest():
        return {"id": row[0], "name": row[1], "role": row[2]}
    return None

def add_user(username, name, role):
    pwd = secrets.token_urlsafe(8)
    h = hashlib.sha256(pwd.encode()).hexdigest()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, name, role, password_hash) VALUES (?,?,?,?)",
                  (username, name, role, h))
        conn.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False
        pwd = None
    conn.close()
    return ok, pwd

init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("📊 SAIS Analyzer — Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        user = check_login(u, p)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials")
else:
    user = st.session_state.user
    st.sidebar.success(f"Logged in: {user['name']} ({user['role']})")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    if user['role'] == 'admin':
        st.title("🛠️ Admin Panel")
        st.subheader("Add New User")
        nu = st.text_input("Username")
        nn = st.text_input("Full Name")
        nr = st.selectbox("Role", ["teacher", "admin"])
        if st.button("Create User"):
            if nu and nn:
                ok, gen_pwd = add_user(nu, nn, nr)
                if ok:
                    st.success(f"✅ User **{nu}** created! Generated password: `{gen_pwd}` (share securely)")
                else:
                    st.error("❌ Username already exists")
        st.subheader("Existing Users")
        conn = sqlite3.connect(DB)
        users = conn.execute("SELECT username, name, role FROM users").fetchall()
        conn.close()
        st.table(users)
    else:
        st.title(f"👋 Welcome, {user['name']}")
        st.info("Teacher analysis tools will be connected in the next steps.")
