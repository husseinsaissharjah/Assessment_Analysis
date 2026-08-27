import streamlit as st
import sqlite3
import hashlib
import secrets
import pandas as pd
import io

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

def db_exec(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.execute(sql, params)
    conn.commit()
    conn.close()

def db_query(sql, params=()):
    conn = sqlite3.connect(DB)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows

def clean_val(x):
    if x is None: return ""
    if pd.isna(x): return ""
    s = str(x).strip()
    if s.endswith(".0"): s = s[:-2]
    return s

def get_id(table, column, value):
    v = clean_val(value).lower()
    if v == "": return None
    rows = db_query(f"SELECT id, {column} FROM {table}")
    for r in rows:
        if clean_val(r[1]).lower() == v:
            return r[0]
    return None

def check_login(username, password):
    row = db_query("SELECT id, name, role, password_hash FROM users WHERE username=?", (username,))
    if row and row[0][3] == hashlib.sha256(password.encode()).hexdigest():
        return {"id": row[0][0], "name": row[0][1], "role": row[0][2]}
    return None

def add_user(username, name, role):
    pwd = secrets.token_urlsafe(8)
    h = hashlib.sha256(pwd.encode()).hexdigest()
    try:
        db_exec("INSERT INTO users (username, name, role, password_hash) VALUES (?,?,?,?)", (username, name, "teacher" if role=="teacher" else "admin", h))
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
        tab = st.sidebar.radio("Admin Menu", ["Users", "Sections", "Subjects", "Semesters/Years", "Mark Components", "Bulk Students"])

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
            st.dataframe(pd.DataFrame(db_query("SELECT username, name, role FROM users"), columns=["Username","Name","Role"]))

        elif tab == "Sections":
            st.subheader("Add Section")
            sn = st.text_input("Section Name")
            gd = st.selectbox("Gender", ["Boys", "Girls", "Mixed"])
            lv = st.selectbox("Level", ["KG", "Elementary", "Middle", "High School"])
            if st.button("Add Section"):
                if sn:
                    db_exec("INSERT INTO sections (section_name, gender, level) VALUES (?,?,?)", (sn, gd, lv))
                    st.success("Section added")
            st.subheader("Sections")
            st.dataframe(pd.DataFrame(db_query("SELECT section_name, gender, level FROM sections"), columns=["Section","Gender","Level"]))

        elif tab == "Subjects":
            st.subheader("Add Subject")
            sb = st.text_input("Subject Name")
            if st.button("Add Subject"):
                if sb:
                    db_exec("INSERT INTO subjects (subject_name) VALUES (?)", (sb,))
                    st.success("Subject added")
            st.subheader("Subjects")
            st.dataframe(pd.DataFrame(db_query("SELECT subject_name FROM subjects"), columns=["Subject"]))

        elif tab == "Semesters/Years":
            st.subheader("Add Semester")
            sm = st.text_input("Semester (e.g. S1)")
            if st.button("Add Semester"):
                if sm: db_exec("INSERT INTO semesters (name) VALUES (?)", (sm,))
            st.subheader("Add Academic Year")
            ay = st.text_input("Year (e.g. 2024-2025)")
            if st.button("Add Year"):
                if ay: db_exec("INSERT INTO academic_years (year) VALUES (?)", (ay,))
            st.subheader("Semesters / Years")
            st.dataframe(pd.DataFrame(db_query("SELECT name FROM semesters"), columns=["Semester"]))
            st.dataframe(pd.DataFrame(db_query("SELECT year FROM academic_years"), columns=["Year"]))

        elif tab == "Mark Components":
            st.subheader("Add Component (Quiz/Test/Final)")
            mc = st.text_input("Component Name")
            if st.button("Add Component"):
                if mc: db_exec("INSERT INTO mark_components (name) VALUES (?)", (mc,))
            st.subheader("Existing Components")
            st.dataframe(pd.DataFrame(db_query("SELECT id, name FROM mark_components"), columns=["ID","Component"]))
            del_id = st.number_input("Component ID to remove", min_value=1, step=1)
            if st.button("Remove Component"):
                db_exec("DELETE FROM mark_components WHERE id=?", (del_id,))
                st.success("Removed")

        elif tab == "Bulk Students":
            st.subheader("📥 Download Template")
            comps = db_query("SELECT name FROM mark_components")
            comp_names = [c[0] for c in comps] if comps else ["Quiz 1", "Quiz 2", "Test", "Final"]
            cols = ["Student ID", "Student Name", "Class", "Section", "Gender", "Subject", "Semester", "Academic Year"] + comp_names
            tpl = pd.DataFrame(columns=cols)
            buf = io.BytesIO()
            tpl.to_excel(buf, index=False)
            st.download_button("Download Excel Template", buf.getvalue(), "student_template.xlsx")

            st.subheader("✅ Allowed values (copy exactly)")
            st.caption("Sections: " + ", ".join([s[0] for s in db_query("SELECT section_name FROM sections")]))
            st.caption("Subjects: " + ", ".join([s[0] for s in db_query("SELECT subject_name FROM subjects")]))
            st.caption("Semesters: " + ", ".join([s[0] for s in db_query("SELECT name FROM semesters")]))
            st.caption("Years: " + ", ".join([s[0] for s in db_query("SELECT year FROM academic_years")]))

            st.subheader("📤 Upload Filled Excel")
            up = st.file_uploader("Upload", type=["xlsx", "xls"], key="bulk")
            if up:
                df = pd.read_excel(up)
                errs = []
                for i, row in df.iterrows():
                    sid = clean_val(row["Student ID"])
                    sname = clean_val(row["Student Name"])
                    cls = clean_val(row["Class"])
                    sec = clean_val(row["Section"])
                    gen = clean_val(row["Gender"])
                    subj = clean_val(row["Subject"])
                    sem = clean_val(row["Semester"])
                    yr = clean_val(row["Academic Year"])
                    sec_id = get_id("sections", "section_name", sec)
                    subj_id = get_id("subjects", "subject_name", subj)
                    sem_id = get_id("semesters", "name", sem)
                    yr_id = get_id("academic_years", "year", yr)
                    if None in (sec_id, subj_id, sem_id, yr_id):
                        errs.append(f"Row {i+2}: Section='{sec}', Subject='{subj}', Sem='{sem}', Year='{yr}' not matched")
                        continue
                    existing = db_query("SELECT id, section_id, level FROM students WHERE student_id=?", (sid,))
                    if not existing:
                        lv = db_query("SELECT level FROM sections WHERE id=?", (sec_id,))[0][0]
                        db_exec("INSERT INTO students (student_id, name, class, section_id, level, gender) VALUES (?,?,?,?,?,?)",
                                (sid, sname, cls, sec_id, lv, gen))
                        stu_db_id = db_query("SELECT id FROM students WHERE student_id=?", (sid,))[0][0]
                    else:
                        stu_db_id = existing[0][0]
                    for comp in comp_names:
                        val = row.get(comp)
                        if pd.notna(val) and clean_val(val) != "":
                            comp_id = get_id("mark_components", "name", comp)
                            if comp_id:
                                db_exec("INSERT INTO marks (student_id, subject_id, semester_id, year_id, component_id, value) VALUES (?,?,?,?,?,?)",
                                        (stu_db_id, subj_id, sem_id, yr_id, comp_id, float(clean_val(val))))
                if errs:
                    st.error("Errors:\n" + "\n".join(errs))
                else:
                    st.success("✅ All students and marks imported!")

    else:
        st.title(f"👋 Welcome, {user['name']}")
        st.info("Analyzer tools will be connected soon.")
