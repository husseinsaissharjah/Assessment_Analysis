import streamlit as st
import sqlite3
import hashlib
import secrets

DB = "sais.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT,
        role TEXT NOT NULL,
        password_hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_name TEXT NOT NULL,
        gender TEXT,
        level TEXT
    );
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        name TEXT,
        class TEXT,
        section_id INTEGER,
        level TEXT,
        gender TEXT
    );
    CREATE TABLE IF NOT EXISTS semesters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );
    CREATE TABLE IF NOT EXISTS academic_years (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year TEXT
    );
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT
    );
    CREATE TABLE IF NOT EXISTS mark_components (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        semester_id INTEGER,
        year_id INTEGER,
        component_id INTEGER,
        value REAL
    );
    ''')
    cur = c.execute("SELECT COUNT(*) FROM users WHERE username=?", ("admin",))
    if cur.fetchone()[0] == 0:
        h = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, name, role, password_hash) VALUES (?,?,?,?)",
                  ("admin", "Administrator", "admin", h))
    conn.commit()
    conn.close()

def check_login(username, password):
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT id, name, role, password_hash FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and row[3] == hashlib.sha256(password.encode()).hexdigest():
        return {"id": row[0], "name": row[1], "role": row[2]}
    return None

def add_user(username, name, role):
    pwd = secrets.token_urlsafe(8)
    h = hashlib.sha256(pwd.encode()).hexdigest()
    try:
        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO users (username, name, role, password_hash) VALUES (?,?,?,?)", (username, name, role, h))
        conn.commit(); conn.close()
        return True, pwd
    except sqlite3.IntegrityError:
        return False, None

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
        tab = st.sidebar.radio("Admin Menu", ["Users", "Sections", "Subjects", "Semesters/Years", "Mark Components"])

        if tab == "Users":
            st.subheader("Add User")
            nu = st.text_input("Username")
            nn = st.text_input("Full Name")
            nr = st.selectbox("Role", ["teacher", "admin"])
            if st.button("Create User"):
                if nu and nn:
                    ok, pwd = add_user(nu, nn, nr)
                    if ok: st.success(f"✅ Created `{nu}` | Password: `{pwd}`")
                    else: st.error("Username exists")
            st.subheader("All Users")
            st.table(sqlite3.connect(DB).execute("SELECT username, name, role FROM users").fetchall())

        elif tab == "Sections":
            st.subheader("Add Section")
            sn = st.text_input("Section Name")
            gd = st.selectbox("Gender", ["Boys", "Girls", "Mixed"])
            lv = st.selectbox("Level", ["KG", "Elementary", "Middle", "High School"])
            if st.button("Add Section"):
                if sn:
                    sqlite3.connect(DB).execute("INSERT INTO sections (section_name, gender, level) VALUES (?,?,?)", (sn, gd, lv))
                    st.success("Section added")
            st.subheader("Sections")
            st.table(sqlite3.connect(DB).execute("SELECT section_name, gender, level FROM sections").fetchall())

        elif tab == "Subjects":
            st.subheader("Add Subject")
            sb = st.text_input("Subject Name")
            if st.button("Add Subject"):
                if sb:
                    sqlite3.connect(DB).execute("INSERT INTO subjects (subject_name) VALUES (?)", (sb,))
                    st.success("Subject added")
            st.subheader("Subjects")
            st.table(sqlite3.connect(DB).execute("SELECT subject_name FROM subjects").fetchall())

        elif tab == "Semesters/Years":
            st.subheader("Add Semester")
            sm = st.text_input("Semester (e.g. S1)")
            if st.button("Add Semester"):
                if sm: sqlite3.connect(DB).execute("INSERT INTO semesters (name) VALUES (?)", (sm,))
            st.subheader("Add Academic Year")
            ay = st.text_input("Year (e.g. 2024-2025)")
            if st.button("Add Year"):
                if ay: sqlite3.connect(DB).execute("INSERT INTO academic_years (year) VALUES (?)", (ay,))
            st.subheader("Semesters / Years")
            st.write(sqlite3.connect(DB).execute("SELECT name FROM semesters").fetchall())
            st.write(sqlite3.connect(DB).execute("SELECT year FROM academic_years").fetchall())

        elif tab == "Mark Components":
            st.subheader("Add Component (Quiz/Test/Final)")
            mc = st.text_input("Component Name")
            if st.button("Add Component"):
                if mc: sqlite3.connect(DB).execute("INSERT INTO mark_components (name) VALUES (?)", (mc,))
            st.subheader("Existing Components")
            comps = sqlite3.connect(DB).execute("SELECT id, name FROM mark_components").fetchall()
            st.table(comps)
            del_id = st.number_input("Component ID to remove", min_value=1, step=1)
            if st.button("Remove Component"):
                sqlite3.connect(DB).execute("DELETE FROM mark_components WHERE id=?", (del_id,))
                st.success("Removed")
    else:
        st.title(f"👋 Welcome, {user['name']}")
        st.info("Analyzer tools will be connected soon.")
