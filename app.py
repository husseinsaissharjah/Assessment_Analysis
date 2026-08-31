import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os

st.set_page_config(page_title="Assessment Analysis", page_icon="📊", layout="wide")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📊 Overview",
        "📝 Objective Analysis",
        "📈 Class Total Average Analysis",
        "🗺️ MAP Analysis",
        "🎯 Achievement & Gaps",
        "📑 Reports"
    ]
)

COLORS = {'Absent':'#808080','Fail':'#d62728','Acceptable':'#ff7f0e','Good':'#2ca02c','Very Good':'#1f77b4','Outstanding':'#9467bd'}
ORDER = ['Absent','Fail','Acceptable','Good','Very Good','Outstanding']

def color_cell(v):
    if v == 'Growth': return 'background-color: green; color: white'
    if v == 'Decay': return 'background-color: red; color: white'
    if v == 'Same': return 'background-color: yellow'
    return ''

def support_level(pct):
    if pct is None: return 'N/A'
    try:
        p = float(pct)
    except:
        return 'N/A'
    if pd.isna(p): return 'N/A'
    return "Intervention" if p < 25 else "Monitor" if p < 50 else "On Track" if p < 75 else "Enrichment"

def objectives_template():
    data = [
        ["Teacher Name: Example Teacher", "Class: Grade 7A", "Date: 27/08/2026", "Assessment name: Quiz 1", "Subject: Mathematics"],
        ["Student Name", "Objective 1", "Objective 2", "Objective 3", ""],
        ["", "Fractions", "Algebra", "Geometry", ""],
        ["Points for Objectives", 10, 15, 5, ""],
        ["Student 1", 8, 12, 4, ""],
        ["Student 2", 10, 14, 5, ""],
        ["Student 3", "A", "A", "A", ""]
    ]
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Assessment"
    for r in data:
        ws.append(r)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def total_template():
    data = [
        ["Teacher Name: Example Teacher", "Class: Grade 7A", "Date: 27/08/2026", "Assessment name: Internal Assessment", "Subject: Mathematics"],
        ["Student Name", "Total"],
        ["Total", 100],
        ["Student 1", 82],
        ["Student 2", 91],
        ["Student 3", 65]
    ]
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Assessment"
    for r in data:
        ws.append(r)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def gaps_template():
    data = [
        ["Teacher Name: Example Teacher", "Class: Grade 7A", "Date: 27/08/2026", "Assessment name: Internal vs MAP", "Subject: Mathematics"],
        ["Student Name", "Total of Internal", "Percentile of MAP"],
        ["Over", 100, ""],
        ["Student 1", 82, 75],
        ["Student 2", 91, 88],
        ["Student 3", 65, 50]
    ]
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Assessment"
    for r in data:
        ws.append(r)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def map_template():
    data = {"Student Name":["Student 1","Student 2","Student 3","Student 4"],"Grade":[7,7,7,7],"Subject":["Mathematics","Mathematics","Mathematics","Mathematics"],"Previous RIT":[205,210,198,215],"Current RIT":[210,214,200,218],"Percentile":[55,70,40,85]}
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="MAP Data")
    buffer.seek(0)
    return buffer.getvalue()

def read_objectives_file(f):
    meta_raw = pd.read_excel(f, nrows=1, header=None)
    f.seek(0)
    meta = {}
    for c in meta_raw.columns:
        val = str(meta_raw.iloc[0, c]).strip()
        if ':' in val:
            k, v = val.split(':', 1)
            meta[k.strip()] = v.strip()
    df = pd.read_excel(f, header=1)
    if str(df.iloc[0, 0]).strip().lower() != "points for objectives":
        df = df.iloc[1:].reset_index(drop=True)
    mask = df.iloc[:, 0].astype(str).str.contains("Points for Objectives", case=False, na=False)
    if not mask.any():
        return None, None
    max_row = df[mask].iloc[0]
    raw_obj_cols = [c for c in df.columns if c != 'Student Name']
    valid_cols = []
    total_max = 0.0
    for c in raw_obj_cols:
        hdr = str(c).strip()
        mx_raw = max_row[c]
        mx_str = str(mx_raw).strip()
        if hdr != '' and hdr.lower() != 'nan' and not hdr.startswith('Unnamed') and mx_str != '' and mx_str.lower() != 'nan':
            try: mx = float(mx_raw)
            except: mx = 0.0
            if mx > 0:
                valid_cols.append(c)
                total_max += mx
    obj_cols = valid_cols
    df = df[~mask].copy()
    df = df.dropna(subset=[df.columns[0]])
    df = df.rename(columns={df.columns[0]: 'Student Name'})
    if obj_cols:
        df = df[['Student Name'] + obj_cols]
    for c in obj_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['Obtained'] = df[obj_cols].sum(axis=1) if obj_cols else 0
    df['Pct'] = (df['Obtained'] / total_max * 100).round(1) if total_max else 0.0
    return meta, df

def read_total_file(f):
    raw = pd.read_excel(f, header=None)
    meta = {}
    for c in raw.iloc[0, :]:
        val = str(c).strip()
        if ':' in val:
            k, v = val.split(':', 1)
            meta[k.strip()] = v.strip()
    headers = [str(x).strip() for x in raw.iloc[1, :].tolist()]
    total_idx = None
    for i in range(2, len(raw)):
        if 'total' in str(raw.iloc[i, 0]).lower():
            total_idx = i
            break
    if total_idx is None:
        return None, None
    try: max_total = float(raw.iloc[total_idx, 1])
    except: max_total = 100.0
    data = raw.iloc[2:, :].copy()
    data.columns = headers
    data = data[data.iloc[:, 0].astype(str).str.lower().str.contains('total') == False]
    data = data.rename(columns={data.columns[0]: 'Student Name'})
    total_col = [c for c in data.columns if 'total' in str(c).lower()]
    if not total_col:
        return None, None
    total_col = total_col[0]
    data[total_col] = pd.to_numeric(data[total_col], errors='coerce').fillna(0)
    data['Pct'] = (data[total_col] / max_total * 100).round(1) if max_total else 0.0
    return meta, data

def read_gaps_file(f):
    raw = pd.read_excel(f, header=None)
    meta = {}
    for c in raw.iloc[0, :]:
        val = str(c).strip()
        if ':' in val:
            k, v = val.split(':', 1)
            meta[k.strip()] = v.strip()
    headers = [str(x).strip() for x in raw.iloc[1, :].tolist()]
    total_idx = None
    for i in range(2, len(raw)):
        if 'over' in str(raw.iloc[i, 0]).lower():
            total_idx = i
            break
    if total_idx is None:
        return None, None
    try: max_total = float(raw.iloc[total_idx, 1])
    except: max_total = 100.0
    data = raw.iloc[2:, :].copy()
    data.columns = headers
    data = data[data.iloc[:, 0].astype(str).str.lower().str.contains('total') == False]
    data = data.rename(columns={data.columns[0]: 'Student Name'})
    internal_col = [c for c in data.columns if 'total of internal' in str(c).lower()]
    map_col = [c for c in data.columns if 'percentile of map' in str(c).lower()]
    if not internal_col or not map_col:
        return None, None
    internal_col = internal_col[0]
    map_col = map_col[0]
    data[internal_col] = pd.to_numeric(data[internal_col], errors='coerce').fillna(0)
    data[map_col] = pd.to_numeric(data[map_col], errors='coerce').fillna(0)
    data['Pct1'] = (data[internal_col] / max_total * 100).round(1) if max_total else 0.0
    data['Pct2'] = data[map_col].round(1)
    return meta, data[['Student Name', 'Pct1', 'Pct2']]

def read_section_file(f):
    meta, df = read_objectives_file(f)
    if meta is None:
        return None, None, None, None, None
    f.seek(0)
    raw_full = pd.read_excel(f, header=1)
    if str(raw_full.iloc[0, 0]).strip().lower() != "points for objectives":
        desc_row = raw_full.iloc[0]
        max_row = raw_full.iloc[1]
    else:
        desc_row = None
        max_row = raw_full.iloc[0]
    obj_names = [c for c in df.columns if c not in ['Student Name', 'Obtained', 'Pct']]
    obj_max = {}
    obj_desc = {}
    for c in obj_names:
        try:
            mx = float(max_row[c])
        except:
            mx = 0
        obj_max[c] = mx
        if desc_row is not None:
            d = str(desc_row[c]).strip()
            if d == '' or d.lower() == 'nan':
                d = str(c)
        else:
            d = str(c)
        obj_desc[c] = d
    return meta, df, obj_names, obj_max, obj_desc

if page == "🏠 Home":
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    st.title("Assessment Analysis")
    st.markdown("### Student Assessment & Achievement Dashboard")
    st.markdown("Analyze MAP, internal assessments, grades, and student performance in seconds.")
    st.markdown("---")
    st.markdown("### 📌 How to use")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("### ① Upload Data\nUpload your Excel files with student marks.")
    with c2: st.markdown("### ② Choose Analysis\nPick the analysis type from the sidebar.")
    with c3: st.markdown("### ③ View Insights\nSee charts, gaps, and download reports.")
    st.info("Use the sidebar on the left to navigate to your analysis.")

elif page == "📊 Overview":
    st.title("📊 Assessment Analysis Overview")
    st.markdown("The Assessment Analysis tool is designed to help teachers, coordinators, and school leaders analyze student achievement quickly and consistently.")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("📝 Objective Analysis")
        st.write("Analyze one assessment at a time using learning objectives and student marks.")
        st.markdown("- Calculate student totals and percentages.\n- Identify absent students.\n- Classify student achievement levels.\n- View bar and pie charts.\n- Download the final analysis as Excel.")
    with c2:
        st.subheader("📈 Class Total Average Analysis")
        st.write("Compare multiple assessments for the same group of students and monitor their academic progress.")
        st.markdown("- Compare assessment results.\n- Convert scores to percentages.\n- Identify student growth.\n- Identify student decay.\n- Identify students with stable performance.\n- View grade performance trends.")
    with c3:
        st.subheader("🎯 Achievement & Gaps")
        st.write("Compare Internal Assessment results with MAP Percentile in one sheet to identify achievement gaps.")
        st.markdown("- Upload one sheet with Internal Total and MAP Percentile.\n- Identify performance gaps.\n- Identify Growth, Decay, and Same performance.\n- Support intervention planning.\n- Download comparison reports.")
    st.markdown("---")
    st.subheader("🗺️ MAP Analysis")
    st.markdown("The MAP Analysis service helps analyze student performance using MAP Growth RIT scores.")
    st.info("**What is a RIT Score?**\n\nA RIT score is the scale used in MAP Growth to measure a student's academic achievement and instructional level.")

elif page == "📝 Objective Analysis":
    st.header("📝 Objective Analysis")
    st.markdown("Analyze a single assessment based on learning objectives and student marks.")
    st.download_button("📥 Download Excel Template", objectives_template(), "Student_Analysis_Template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("---")
    st.header("Step 1: Upload Student Marks Excel")
    st.info("Row 1: Assessment Information\nRow 2: Headers (Objective names)\nRow 3: Objective Descriptions\nRow 4: 'Points for Objectives' + Maximum Marks\nRow 5+: Student Marks\nLeave empty or enter 'A' for absent students.")
    up_file = st.file_uploader("Upload Excel", type=["xlsx", "xls"], key="single")
    if up_file:
        meta_raw = pd.read_excel(up_file, nrows=1, header=None)
        up_file.seek(0)
        meta_info = {}
        for c in meta_raw.columns:
            val = str(meta_raw.iloc[0, c]).strip()
            if ':' in val:
                k, v = val.split(':', 1)
                meta_info[k.strip()] = v.strip()
        st.subheader("📋 Info")
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"**👩‍🏫 Teacher:** {meta_info.get('Teacher Name', 'N/A')}")
        m2.markdown(f"**🏫 Class:** {meta_info.get('Class', 'N/A')}")
        m3.markdown(f"**📅 Date:** {meta_info.get('school', 'N/A')}" if False else f"**📅 Date:** {meta_info.get('Date', 'N/A')}")
        m4.markdown(f"**📝 Assessment:** {meta_info.get('Assessment name', 'N/A')}")
        st.markdown(f"### 📝 Name: **{meta_info.get('Assessment name', 'N/A')}** | 📚 Subject: **{meta_info.get('Subject', 'N/A')}**")
        raw = pd.read_excel(up_file, header=1)
        if str(raw.iloc[0, 0]).strip().lower() != "points for objectives":
            desc_row = raw.iloc[0]
            raw_students = raw.iloc[1:].reset_index(drop=True)
        else:
            desc_row = None
            raw_students = raw.copy()
        obj_desc = {}
        for c in raw.columns:
            if c != 'Student Name':
                if desc_row is not None:
                    d = str(desc_row[c]).strip()
                    if d == '' or d.lower() == 'nan': d = str(c)
                else:
                    d = str(c)
                obj_desc[c] = d
        all_obj_names = [c for c in raw_students.columns if c != 'Student Name']
        mask = raw_students.iloc[:, 0].astype(str).str.contains("Points for Objectives", case=False, na=False)
        if not mask.any():
            st.error("❌ Need 'Points for Objectives' row."); st.stop()
        max_row = raw_students[mask].iloc[0]
        obj_names = []
        obj_max = []
        for c in all_obj_names:
            hdr = str(c).strip()
            mx_raw = max_row[c]
            mx_str = str(mx_raw).strip()
            if hdr != '' and hdr.lower() != 'nan' and not hdr.startswith('Unnamed') and mx_str != '' and mx_str.lower() != 'nan':
                try: mx = float(mx_raw)
                except: mx = 0.0
                if mx > 0:
                    obj_names.append(c); obj_max.append(mx)
        student_df = raw_students[~mask].copy().dropna(subset=['Student Name'])
        student_df = student_df[['Student Name'] + obj_names].copy()
        def is_absent(row):
            has_A = False; all_empty = True
            for c in obj_names:
                v = row[c]
                if isinstance(v, str) and 'a' in v.lower(): has_A = True
                elif not (pd.isna(v) or (isinstance(v, str) and v.strip() == '')): all_empty = False
            return has_A or all_empty
        student_df['Absent'] = student_df.apply(is_absent, axis=1)
        for c in obj_names:
            student_df[c] = pd.to_numeric(student_df[c], errors='coerce').fillna(0)
        total_max = sum(obj_max)
        st.info(f"📋 Auto Total Max Mark = **{total_max}**")
        st.markdown("### 📚 Objectives")
        for i, obj in enumerate(obj_names, 1):
            st.markdown(f"{i}. **{obj}** – {obj_desc.get(obj, obj)}")
        errors = []
        for _, row in student_df.iterrows():
            if row['Absent']: continue
            for j, c in enumerate(obj_names):
                if row[c] > obj_max[j]: errors.append(f"• {row['Student Name']}: {c}={row[c]} > max {obj_max[j]}")
                if row[c] < 0: errors.append(f"• {row['Student Name']}: {c} Negative")
        st.subheader("📊 Preview")
        st.dataframe(student_df, use_container_width=True)
        if errors:
            st.error("🚫 Fix data entry:\n" + "\n".join(errors))
        else:
            if st.button("Analyze Assessment"):
                res = []
                for _, row in student_df.iterrows():
                    if row['Absent']:
                        res.append({'Student Name': row['Student Name'], 'Total': '-', 'Total %': None, 'Level': 'Absent'}); continue
                    ps = []; tot = 0
                    for j, c in enumerate(obj_names):
                        mk = float(row[c]); tot += mk; ps.append((mk / obj_max[j]) * 100 if obj_max[j] else 0)
                    tp = sum(ps) / len(ps)
                    lvl = 'Fail' if tp < 60 else 'Acceptable' if tp < 70 else 'Good' if tp < 80 else 'Very Good' if tp < 90 else 'Outstanding'
                    res.append({'Student Name': row['Student Name'], 'Total': tot, 'Total %': round(tp, 1), 'Level': lvl})
                rdf = pd.DataFrame(res)
                rdf['Support Level'] = rdf['Total %'].apply(support_level)
                st.header("Step 2: Analysis Report")
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                cnt = rdf['Level'].value_counts().to_dict()
                c1.metric("Absent", cnt.get('Absent', 0))
                c2.metric("Fail", cnt.get('Fail', 0))
                c3.metric("Acceptable", cnt.get('Acceptable', 0))
                c4.metric("Good", cnt.get('Good', 0))
                c5.metric("Very Good", cnt.get('Very Good', 0))
                c6.metric("Outstanding", cnt.get('Outstanding', 0))
                ts = len(rdf)
                ge60 = (rdf['Total %'] >= 60).sum() / ts * 100 if ts else 0
                gt60 = (rdf['Total %'] > 60).sum() / ts * 100 if ts else 0
                gt75 = (rdf['Total %'] > 75).sum() / ts * 100 if ts else 0
                ov = "Outstanding" if gt75 >= 90 else "Very Good" if gt60 >= 90 else "Good" if gt60 >= 75 else "Acceptable" if ge60 >= 60 else "Below Acceptable"
                st.success(f"**{ov}** (Max {total_max})")
                cdf = rdf['Level'].value_counts().reset_index(); cdf.columns = ['Level', 'Count']
                cdf['Level'] = pd.Categorical(cdf['Level'], categories=ORDER, ordered=True); cdf = cdf.sort_values('Level')
                v1, v2 = st.columns(2)
                with v1:
                    st.subheader("📊 Student Achievement")
                    st.plotly_chart(px.bar(rdf.dropna(subset=['Total %']), x='Student Name', y='Total %', color='Level', range_y=[0, 100]), use_container_width=True)
                with v2:
                    st.subheader("📊 Level Distribution")
                    st.plotly_chart(px.pie(cdf, names='Level', values='Count', color='Level', color_discrete_map=COLORS, hole=0.3), use_container_width=True)
                st.subheader("🎯 Student Support Levels")
                st.plotly_chart(px.bar(rdf.dropna(subset=['Total %']), x='Student Name', y='Total %', color='Support Level', range_y=[0, 100]), use_container_width=True)
                support_count = rdf['Support Level'].value_counts().reset_index(); support_count.columns = ['Support Level', 'Students']
                st.subheader("👥 Support Groups")
                st.dataframe(support_count, use_container_width=True)
                st.dataframe(rdf, use_container_width=True)
                eb = io.BytesIO(); rdf.to_excel(eb, index=False)
                st.download_button("📊 Download Excel", eb.getvalue(), "Report.xlsx")

elif page == "📈 Class Total Average Analysis":
    st.header("📈 Class Total Average Analysis")
    st.markdown("Compare multiple assessments for the same class and monitor the class average progress over time.")
    st.download_button("📥 Download Excel Template", objectives_template(), "Grade_Analysis_Template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.info("Choose the number of assessments. Upload files using the same Excel format as Objective Analysis. Each assessment score will automatically be converted to a percentage before comparison.")
    n_assess = st.number_input("🔢 Number of assessments", min_value=2, max_value=10, value=2, step=1, key="nass")
    files = []
    for i in range(int(n_assess)):
        files.append(st.file_uploader(f"📄 Assessment {i}", type=["xlsx", "xls"], key=f"up{i}"))
    if all(files):
        metas = []; merged = None; pct_cols = []; names = []; descriptions = []
        for i, f in enumerate(files):
            meta, df = read_objectives_file(f)
            if meta is None:
                st.error(f"❌ File {i + 1} missing 'Points for Objectives' row."); st.stop()
            f.seek(0)
            raw_g = pd.read_excel(f, header=1)
            if str(raw_g.iloc[0, 0]).strip().lower() != "points for objectives":
                desc_row_g = raw_g.iloc[0]
            else:
                desc_row_g = None
            obj_desc_g = {}
            for c in raw_g.columns:
                if c != 'Student Name':
                    if desc_row_g is not None:
                        d = str(desc_row_g[c]).strip()
                        if d == '' or d.lower() == 'nan': d = str(c)
                    else:
                        d = str(c)
                    obj_desc_g[c] = d
            metas.append(meta)
            names.append(meta.get('Assessment name', 'N/A'))
            descriptions.append(obj_desc_g)
            col = f'Pct{i + 1}'
            keep = df[['Student Name', 'Pct']].rename(columns={'Pct': col})
            merged = keep if merged is None else pd.merge(merged, keep, on='Student Name', how='outer')
            pct_cols.append(col)
        st.subheader("📋 Assessment Information")
        for i, m in enumerate(metas):
            st.markdown(f"**File {i + 1} ({m.get('Assessment name', 'N/A')}):** 👩‍🏫 {m.get('Teacher Name', 'N/A')} | 🏫 {m.get('Class', 'N/A')} | 📅 {m.get('Date', 'N/A')} | 📚 {m.get('Subject', 'N/A')}")
            st.markdown("**📚 Objectives:**")
            for c, d in descriptions[i].items():
                st.markdown(f"- **{c}** – {d}")
        st.markdown(f"### 📊 Comparing: **{' / '.join(names)}** | 📚 Subject: **{metas[0].get('Subject', 'N/A')}**")
        merged[pct_cols] = merged[pct_cols].fillna(0)
        merged['Difference'] = (merged[pct_cols[-1]] - merged[pct_cols[0]]).round(1)
        merged['Status'] = merged['Difference'].apply(lambda d: 'Growth' if d > 0.5 else 'Decay' if d < -0.5 else 'Same')
        merged['Support Level'] = merged[pct_cols[-1]].apply(support_level)
        st.subheader("📊 Comparison Table (Percentage Based)")
        st.dataframe(merged.style.map(color_cell, subset=['Status']), use_container_width=True)
        cnt = merged['Status'].value_counts().to_dict()
        gc = cnt.get('Growth', 0); dc = cnt.get('Decay', 0); sc = cnt.get('Same', 0)
        st.subheader("📢 Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("🟩 Growth", gc); m2.metric("🟥 Decay", dc); m3.metric("🟨 Same", sc)
        cd = pd.DataFrame({'Status': ['Growth', 'Decay', 'Same'], 'Count': [gc, dc, sc]})
        cd['Status'] = pd.Categorical(cd['Status'], categories=['Decay', 'Same', 'Growth'], ordered=True)
        v1, v2 = st.columns(2)
        with v1:
            st.markdown("**Bar Chart**")
            st.plotly_chart(px.bar(cd, x='Status', y='Count', color='Status', color_discrete_map={'Growth': 'green', 'Decay': 'red', 'Same': 'yellow'}), use_container_width=True)
        with v2:
            st.markdown("**Pie Chart**")
            pf = px.pie(cd, names='Status', values='Count', color='Status', color_discrete_map={'Growth': 'green', 'Decay': 'red', 'Same': 'yellow'}, hole=0.3)
            pf.update_traces(textinfo='percent+label'); st.plotly_chart(pf, use_container_width=True)
        avg = merged[pct_cols].mean().reset_index(); avg.columns = ['Assessment', 'Average']
        avg['Assessment'] = avg['Assessment'].str.replace('Pct', 'Assess')
        st.subheader("📈 Average Score Trend (%)")
        st.plotly_chart(px.line(avg, x='Assessment', y='Average', markers=True), use_container_width=True)
        st.subheader("📈 Student Growth (Difference)")
        st.plotly_chart(px.bar(merged, x='Student Name', y='Difference', color='Status'), use_container_width=True)
        support_count = merged['Support Level'].value_counts().reset_index(); support_count.columns = ['Support Level', 'Students']
        st.subheader("👥 Support Groups")
        st.dataframe(support_count, use_container_width=True)
        bufc = io.BytesIO(); merged.to_excel(bufc, index=False)
        st.download_button("📊 Download Comparison Excel", bufc.getvalue(), "Comparison.xlsx")

elif page == "🗺️ MAP Analysis":
    st.title("🗺️ MAP Analysis")
    st.info("### What is a RIT Score?\nThe RIT score is the scale used by MAP Growth to measure student achievement and instructional level.")
    st.markdown("### What this does\n- Calculates RIT growth.\n- Identifies Growth, Decay, or Same performance.\n- Shows student percentile.\n- Calculates grade average RIT.\n- Identifies students below the selected percentile.\n- Identifies students requiring intervention or enrichment.")
    st.download_button("📥 Download MAP Excel Template", map_template(), "MAP_Analysis_Template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("---")
    map_file = st.file_uploader("📄 Upload MAP Data Excel", type=["xlsx", "xls"], key="map")
    if map_file:
        try:
            map_df = pd.read_excel(map_file)
            required_cols = ["Student Name", "Grade", "Subject", "Previous RIT", "Current RIT", "Percentile"]
            missing = [c for c in required_cols if c not in map_df.columns]
            if missing:
                st.error("❌ Missing columns: " + ", ".join(missing)); st.stop()
            map_df["Previous RIT"] = pd.to_numeric(map_df["Previous RIT"], errors="coerce")
            map_df["Current RIT"] = pd.to_numeric(map_df["Current RIT"], errors="coerce")
            map_df["Percentile"] = pd.to_numeric(map_df["Percentile"], errors="coerce")
            map_df["RIT Growth"] = map_df["Current RIT"] - map_df["Previous RIT"]
            map_df["Growth Status"] = map_df["RIT Growth"].apply(lambda x: "Growth" if x > 0 else "Decay" if x < 0 else "Same")
            map_df["Support Level"] = map_df["Percentile"].apply(lambda x: "Intervention" if x < 25 else "Monitor" if x < 50 else "On Track" if x < 75 else "Enrichment")
            st.subheader("📋 MAP Data Preview")
            st.dataframe(map_df, use_container_width=True)
            st.markdown("---")
            st.subheader("📊 MAP Summary")
            total_students = len(map_df)
            avg_previous = map_df["Previous RIT"].mean()
            avg_current = map_df["Current RIT"].mean()
            avg_growth = map_df["RIT Growth"].mean()
            avg_percentile = map_df["Percentile"].mean()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("👥 Students", total_students)
            c2.metric("📉 Previous Avg RIT", round(avg_previous, 1))
            c3.metric("📈 Current Avg RIT", round(avg_current, 1))
            c4.metric("🚀 Average Growth", round(avg_growth, 1))
            st.metric("🎯 Average Percentile", round(avg_percentile, 1))
            st.markdown("---")
            status_count = map_df["Growth Status"].value_counts().reset_index(); status_count.columns = ["Status", "Count"]
            v1, v2 = st.columns(2)
            with v1:
                st.subheader("📈 Student Growth")
                st.plotly_chart(px.bar(map_df, x="Student Name", y="RIT Growth", color="Growth Status"), use_container_width=True)
            with v2:
                st.subheader("📊 Growth Distribution")
                st.plotly_chart(px.pie(status_count, names="Status", values="Count", hole=0.3), use_container_width=True)
            st.markdown("---")
            st.subheader("🎯 Student Percentile")
            st.plotly_chart(px.bar(map_df, x="Student Name", y="Percentile", color="Support Level", range_y=[0, 100]), use_container_width=True)
            st.subheader("👥 Support Groups")
            support_count = map_df["Support Level"].value_counts().reset_index(); support_count.columns = ["Support Level", "Students"]
            st.dataframe(support_count, use_container_width=True)
            st.subheader("📋 Student MAP Analysis")
            st.dataframe(map_df.style.map(color_cell, subset=["Growth Status"]), use_container_width=True)
            map_buffer = io.BytesIO(); map_df.to_excel(map_buffer, index=False)
            st.download_button("📥 Download MAP Analysis", map_buffer.getvalue(), "MAP_Analysis_Report.xlsx")
        except Exception as e:
            st.error(f"❌ Error reading MAP file: {e}")

elif page == "🎯 Achievement & Gaps":
    st.header("🎯 Achievement & Gaps (Internal vs MAP)")
    st.download_button("📥 Download Excel Template", gaps_template(), "Achievement_Gaps_Template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.info(
        "This service compares a class's Internal Assessment total marks with their MAP Percentile "
        "to identify achievement gaps. Upload ONE Excel sheet with columns: "
        "**Student Name**, **Total of Internal**, **Percentile of MAP**. "
        "Row 1: Assessment Information | Row 2: Headers | Row 3: 'Over' + Maximum Mark | Row 4+: Student Marks."
    )
    f = st.file_uploader("📄 Upload Single Sheet", type=["xlsx", "xls"], key="gaps")
    if f:
        m, df = read_gaps_file(f)
        if m is None:
            st.error("❌ File missing required rows/columns (Over / Percentile of MAP)."); st.stop()
        st.subheader("📋 Assessment Information")
        st.markdown(f"👩‍🏫 {m.get('Teacher Name', 'N/A')} | 🏫 {m.get('Class', 'N/A')} | 📅 {m.get('Date', 'N/A')} | 📝 {m.get('Assessment name', 'N/A')} | 📚 {m.get('Subject', 'N/A')}")
        df['Difference'] = (df['Pct2'] - df['Pct1']).round(1)
        df['Status'] = df['Difference'].apply(lambda d: 'Growth' if d > 0.5 else 'Decay' if d < -0.5 else 'Same')
        df['Support Level'] = df['Pct2'].apply(support_level)
        st.subheader("📊 Comparison Table (Percentage Based)")
        st.dataframe(df.style.map(color_cell, subset=['Status']), use_container_width=True)
        cnt = df['Status'].value_counts().to_dict()
        gc = cnt.get('Growth', 0); dc = cnt.get('Decay', 0); sc = cnt.get('Same', 0)
        st.subheader("📢 Summary")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("🟩 Growth", gc); mc2.metric("🟥 Decay", dc); mc3.metric("🟨 Same", sc)
        cd = pd.DataFrame({'Status': ['Growth', 'Decay', 'Same'], 'Count': [gc, dc, sc]})
        cd['Status'] = pd.Categorical(cd['Status'], categories=['Decay', 'Same', 'Growth'], ordered=True)
        v1, v2 = st.columns(2)
        with v1:
            st.markdown("**Bar Chart**")
            st.plotly_chart(px.bar(cd, x='Status', y='Count', color='Status', color_discrete_map={'Growth': 'green', 'Decay': 'red', 'Same': 'yellow'}), use_container_width=True)
        with v2:
            st.markdown("**Pie Chart**")
            pf = px.pie(cd, names='Status', values='Count', color='Status', color_discrete_map={'Growth': 'green', 'Decay': 'red', 'Same': 'yellow'}, hole=0.3)
            pf.update_traces(textinfo='percent+label'); st.plotly_chart(pf, use_container_width=True)
        st.subheader("📈 Student Gap (Difference)")
        st.plotly_chart(px.bar(df, x='Student Name', y='Difference', color='Status'), use_container_width=True)
        support_count = df['Support Level'].value_counts().reset_index(); support_count.columns = ['Support Level', 'Students']
        st.subheader("👥 Support Groups")
        st.dataframe(support_count, use_container_width=True)
        bufc = io.BytesIO(); df.to_excel(bufc, index=False)
        st.download_button("📊 Download Comparison Excel", bufc.getvalue(), "Internal_MAP_Comparison.xlsx")

elif page == "📑 Reports":
    st.title("📑 Reports")
    st.markdown("### 🛠️ Available Services")

    service = st.radio(
        "Select Service",
        ["Compare between sections"],
        key="report_service"
    )

    if service == "Compare between sections":
        st.header("🔍 Compare Between Sections")
        comp_type = st.radio(
            "Comparison Type",
            [
                "By Assessment Objectives",
                "By Assessment Total Mark",
                "By External Benchmark Assessment"
            ],
            key="comparison_type"
        )

        if comp_type == "By Assessment Objectives":
            st.subheader("📚 By Assessment Objectives")
            st.info(
                "Select number of classes, then upload one Objective Analysis "
                "Excel file per class. Bands: Below 60% (Weak), 60-75% (Acceptable), "
                "76-85% (Very Good), 86-100% (Excellent)."
            )
            n_sec = st.number_input("Number of classes", min_value=2, max_value=10, value=2, step=1, key="nsec")
            sec_files = []
            for i in range(int(n_sec)):
                sec_files.append(st.file_uploader(f"📄 Class {i+1} file", type=["xlsx", "xls"], key=f"secfile_{i}"))

            if all(sec_files):
                sections_data = []
                for idx, f in enumerate(sec_files, 1):
                    meta, df, obj_names, obj_max, obj_desc = read_section_file(f)
                    if meta is None:
                        st.error(f"❌ Class {idx} file invalid"); st.stop()
                    class_name = meta.get('Class', f'Class {idx}')
                    st.markdown(f"### 📋 Class {idx} Info")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.markdown(f"**👩‍🏫 Teacher:** {meta.get('Teacher Name', 'N/A')}")
                    m2.markdown(f"**🏫 Class:** {class_name}")
                    m3.markdown(f"**📅 Date:** {meta.get('Date', 'N/A')}")
                    m4.markdown(f"**📝 Assessment:** {meta.get('Assessment name', 'N/A')}")
                    st.markdown(f"**📚 Subject:** {meta.get('Subject', 'N/A')}")
                    st.markdown("**📚 Objectives:**")
                    for c in obj_names:
                        st.markdown(f"- **{c}** – {obj_desc.get(c, c)}")

                    def band(p):
                        if pd.isna(p): return "Below 60% (Weak)"
                        if p < 60: return "Below 60% (Weak)"
                        elif p <= 75: return "60-75% (Acceptable)"
                        elif p <= 85: return "76-85% (Very Good)"
                        else: return "86-100% (Excellent)"
                    df['Band'] = df['Pct'].apply(band)
                    obj_avg = {}
                    for c in obj_names:
                        mx = obj_max[c]
                        if mx > 0:
                            obj_avg[c] = (df[c] / mx * 100).mean()
                        else:
                            obj_avg[c] = 0
                    sections_data.append({
                        'name': class_name,
                        'df': df,
                        'bands': df['Band'].value_counts(),
                        'obj_avg': obj_avg,
                        'obj_names': obj_names,
                        'obj_desc': obj_desc
                    })

                band_order = ["Below 60% (Weak)", "60-75% (Acceptable)", "76-85% (Very Good)", "86-100% (Excellent)"]
                band_df = pd.DataFrame()
                for sd in sections_data:
                    temp = sd['bands'].reindex(band_order).fillna(0).astype(int)
                    temp.name = sd['name']
                    band_df = pd.concat([band_df, temp.to_frame().T], axis=0)
                band_df = band_df[band_order]

                plot_df = band_df.reset_index().melt(id_vars='index', value_vars=band_order)
                plot_df.columns = ['Class', 'Band', 'Count']

                st.subheader("📊 Band Distribution per Class")
                st.plotly_chart(
                    px.bar(plot_df, x='Band', y='Count', color='Class', barmode='group', text='Count'),
                    use_container_width=True
                )

                st.subheader("📈 Dumbbell Chart (Class gap per Band)")
                fig = go.Figure()
                for sec in band_df.index:
                    fig.add_trace(go.Scatter(
                        x=band_df.loc[sec],
                        y=band_order,
                        mode='markers',
                        name=sec,
                        marker=dict(size=14)
                    ))
                for band in band_order:
                    fig.add_trace(go.Scatter(
                        x=band_df[band].values,
                        y=[band]*len(band_df),
                        mode='lines',
                        line=dict(color='lightgray', width=2),
                        showlegend=False
                    ))
                fig.update_layout(xaxis_title="Student Count", yaxis_title="Performance Band", height=400)
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("🏆 Class Order per Objective (Rank 1 = Highest Average %)")
                rank_rows = []
                obj_union = sections_data[0]['obj_names']
                for obj in obj_union:
                    avgs = {sd['name']: sd['obj_avg'].get(obj, 0) for sd in sections_data}
                    sorted_secs = sorted(avgs.items(), key=lambda x: x[1], reverse=True)
                    row = {
                        'Objective': obj,
                        'Description': sections_data[0]['obj_desc'].get(obj, '')
                    }
                    for i, (sname, val) in enumerate(sorted_secs, 1):
                        row[f"Rank {i}"] = f"{sname} ({val:.1f}%)"
                    rank_rows.append(row)
                rank_df = pd.DataFrame(rank_rows)
                st.dataframe(rank_df, use_container_width=True)
                st.success("✅ Comparison complete.")

        elif comp_type == "By Assessment Total Mark":
            st.subheader("📊 By Assessment Total Mark")
            st.info(
                "Upload Objective Analysis (objectives) OR Total Mark sheets per class. "
                "All will be converted to percentage. Bands: Below 60% (Weak), 60-75% (Acceptable), "
                "76-85% (Very Good), 86-100% (Excellent)."
            )
            n_sec = st.number_input("Number of classes", min_value=2, max_value=10, value=2, step=1, key="nsec_total")
            sec_files = []
            for i in range(int(n_sec)):
                sec_files.append(st.file_uploader(f"📄 Class {i+1} file", type=["xlsx", "xls"], key=f"totalfile_{i}"))

            if all(sec_files):
                sections_data = []
                for idx, f in enumerate(sec_files, 1):
                    f.seek(0)
                    raw_check = pd.read_excel(f, header=1)
                    has_total_row = raw_check.iloc[:, 0].astype(str).str.contains("Points for Objectives", case=False, na=False).any()
                    if has_total_row:
                        meta, df = read_objectives_file(f)
                    else:
                        meta, df = read_total_file(f)
                    if meta is None:
                        st.error(f"❌ Class {idx} file invalid (no Pct or Total)"); st.stop()
                    class_name = meta.get('Class', f'Class {idx}')
                    st.markdown(f"### 📋 Class {idx} Info")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.markdown(f"**👩‍🏫 Teacher:** {meta.get('Teacher Name', 'N/A')}")
                    m2.markdown(f"**🏫 Class:** {class_name}")
                    m3.markdown(f"**📅 Date:** {meta.get('Date', 'N/A')}")
                    m4.markdown(f"**📝 Assessment:** {meta.get('Assessment name', 'N/A')}")
                    st.markdown(f"**📚 Subject:** {meta.get('Subject', 'N/A')}")

                    def band(p):
                        if pd.isna(p): return "Below 60% (Weak)"
                        if p < 60: return "Below 60% (Weak)"
                        elif p <= 75: return "60-75% (Acceptable)"
                        elif p <= 85: return "76-85% (Very Good)"
                        else: return "86-100% (Excellent)"
                    df['Band'] = df['Pct'].apply(band)
                    sections_data.append({
                        'name': class_name,
                        'df': df,
                        'bands': df['Band'].value_counts()
                    })

                band_order = ["Below 60% (Weak)", "60-75% (Acceptable)", "76-85% (Very Good)", "86-100% (Excellent)"]
                band_df = pd.DataFrame()
                for sd in sections_data:
                    temp = sd['bands'].reindex(band_order).fillna(0).astype(int)
                    temp.name = sd['name']
                    band_df = pd.concat([band_df, temp.to_frame().T], axis=0)
                band_df = band_df[band_order]

                plot_df = band_df.reset_index().melt(id_vars='index', value_vars=band_order)
                plot_df.columns = ['Class', 'Band', 'Count']

                st.subheader("📊 Band Distribution per Class")
                st.plotly_chart(
                    px.bar(plot_df, x='Band', y='Count', color='Class', barmode='group', text='Count'),
                    use_container_width=True
                )

                st.subheader("📈 Dumbbell Chart (Class gap per Band)")
                fig = go.Figure()
                for sec in band_df.index:
                    fig.add_trace(go.Scatter(
                        x=band_df.loc[sec],
                        y=band_order,
                        mode='markers',
                        name=sec,
                        marker=dict(size=14)
                    ))
                for band in band_order:
                    fig.add_trace(go.Scatter(
                        x=band_df[band].values,
                        y=[band]*len(band_df),
                        mode='lines',
                        line=dict(color='lightgray', width=2),
                        showlegend=False
                    ))
                fig.update_layout(xaxis_title="Student Count", yaxis_title="Performance Band", height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.success("✅ Total Mark comparison complete.")

        elif comp_type == "By External Benchmark Assessment":
            st.subheader("🏢 By External Benchmark Assessment")
            st.info(
                "Upload External Benchmark (objectives or total) sheets per class. "
                "All will be converted to percentage. Bands: Below 60% (Weak), 60-75% (Acceptable), "
                "76-85% (Very Good), 86-100% (Excellent)."
            )
            n_sec = st.number_input("Number of classes", min_value=2, max_value=10, value=2, step=1, key="nsec_ext")
            sec_files = []
            for i in range(int(n_sec)):
                sec_files.append(st.file_uploader(f"📄 Class {i+1} file", type=["xlsx", "xls"], key=f"extfile_{i}"))

            if all(sec_files):
                sections_data = []
                for idx, f in enumerate(sec_files, 1):
                    f.seek(0)
                    raw_check = pd.read_excel(f, header=1)
                    has_total_row = raw_check.iloc[:, 0].astype(str).str.contains("Points for Objectives", case=False, na=False).any()
                    if has_total_row:
                        meta, df = read_objectives_file(f)
                    else:
                        meta, df = read_total_file(f)
                    if meta is None:
                        st.error(f"❌ Class {idx} file invalid (no Pct or Total)"); st.stop()
                    class_name = meta.get('Class', f'Class {idx}')
                    st.markdown(f"### 📋 Class {idx} Info")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.markdown(f"**👩‍🏫 Teacher:** {meta.get('Teacher Name', 'N/A')}")
                    m2.markdown(f"**🏫 Class:** {class_name}")
                    m3.markdown(f"**📅 Date:** {meta.get('Date', 'N/A')}")
                    m4.markdown(f"**📝 Assessment:** {meta.get('Assessment name', 'N/A')}")
                    st.markdown(f"**📚 Subject:** {meta.get('Subject', 'N/A')}")

                    def band(p):
                        if pd.isna(p): return "Below 60% (Weak)"
                        if p < 60: return "Below 60% (Weak)"
                        elif p <= 75: return "60-75% (Acceptable)"
                        elif p <= 85: return "76-85% (Very Good)"
                        else: return "86-100% (Excellent)"
                    df['Band'] = df['Pct'].apply(band)
                    sections_data.append({
                        'name': class_name,
                        'df': df,
                        'bands': df['Band'].value_counts()
                    })

                band_order = ["Below 60% (Weak)", "60-75% (Acceptable)", "76-85% (Very Good)", "86-100% (Excellent)"]
                band_df = pd.DataFrame()
                for sd in sections_data:
                    temp = sd['bands'].reindex(band_order).fillna(0).astype(int)
                    temp.name = sd['name']
                    band_df = pd.concat([band_df, temp.to_frame().T], axis=0)
                band_df = band_df[band_order]

                plot_df = band_df.reset_index().melt(id_vars='index', value_vars=band_order)
                plot_df.columns = ['Class', 'Band', 'Count']

                st.subheader("📊 Band Distribution per Class")
                st.plotly_chart(
                    px.bar(plot_df, x='Band', y='Count', color='Class', barmode='group', text='Count'),
                    use_container_width=True
                )

                st.subheader("📈 Dumbbell Chart (Class gap per Band)")
                fig = go.Figure()
                for sec in band_df.index:
                    fig.add_trace(go.Scatter(
                        x=band_df.loc[sec],
                        y=band_order,
                        mode='markers',
                        name=sec,
                        marker=dict(size=14)
                    ))
                for band in band_order:
                    fig.add_trace(go.Scatter(
                        x=band_df[band].values,
                        y=[band]*len(band_df),
                        mode='lines',
                        line=dict(color='lightgray', width=2),
                        showlegend=False
                    ))
                fig.update_layout(xaxis_title="Student Count", yaxis_title="Performance Band", height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.success("✅ External Benchmark comparison complete.")
