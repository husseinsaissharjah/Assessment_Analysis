import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

st.set_page_config(page_title="SAIS Analyzer", page_icon="📊", layout="wide")

# ---------- Centered Bigger Logo ----------
if os.path.exists("logo.png"):
    try:
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.image("logo.png", width=200)
    except Exception:
        pass

st.title("📊 SAIS Analyzer")

COLORS = {'Absent':'#808080','Fail':'#d62728','Acceptable':'#ff7f0e','Good':'#2ca02c','Very Good':'#1f77b4','Outstanding':'#9467bd'}
ORDER = ['Absent','Fail','Acceptable','Good','Very Good','Outstanding']

# ---------- Helper for Tab 1 & 2 (objectives) ----------
def read_meta_and_pct(f):
    meta_raw = pd.read_excel(f, nrows=1, header=None)
    f.seek(0)
    meta_info = {}
    for c in meta_raw.columns:
        val = str(meta_raw.iloc[0, c]).strip()
        if ':' in val:
            k, v = val.split(':', 1)
            meta_info[k.strip()] = v.strip()
    df = pd.read_excel(f, header=1)
    mask = df.iloc[:, 0].astype(str).str.contains("Points for Objectives", case=False, na=False)
    if not mask.any():
        return None, None
    max_row = df[mask].iloc[0]
    obj_cols = [c for c in df.columns if c != 'Student Name']
    total_max = sum(float(max_row[c]) for c in obj_cols if str(max_row[c]).strip() != '')
    df = df[~mask].copy()
    df = df.rename(columns={df.columns[0]: 'Student Name'})
    for c in obj_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['Obtained'] = df[obj_cols].sum(axis=1)
    df['Pct'] = (df['Obtained'] / total_max * 100).round(1) if total_max else 0.0
    return meta_info, df

# ---------- Helper for Tab 3 (Total column only) ----------
def read_internal_external(f):
    raw = pd.read_excel(f, header=None)
    meta_info = {}
    for c in raw.iloc[0, :]:
        val = str(c).strip()
        if ':' in val:
            k, v = val.split(':', 1)
            meta_info[k.strip()] = v.strip()
    headers = [str(x).strip() for x in raw.iloc[1, :].tolist()]
    total_idx = None
    for i in range(2, len(raw)):
        if 'total' in str(raw.iloc[i, 0]).lower():
            total_idx = i
            break
    if total_idx is None:
        return None, None
    try:
        max_total = float(raw.iloc[total_idx, 1])
    except:
        max_total = 100.0
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
    return meta_info, data

# ---------- Cell color ----------
def color_cell(v):
    if v == 'Growth': return 'background-color: green; color: white'
    if v == 'Decay': return 'background-color: red; color: white'
    if v == 'Same': return 'background-color: yellow'
    return ''

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs([
    "📊 Single Assessment Analysis",
    "🔄 Comparison (Multiple Assessments)",
    "🆚 Internal vs External"
])

# ================= TAB 1 =================
with tab1:
    st.header("Step 1: Upload Student Marks Excel")
    st.info("Row1: Info | Row2: Headers | Row3: 'Points for Objectives' + max marks | Row4+: Marks. Leave empty or put 'A' for absent.")
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
        st.subheader("📋 Assessment Information")
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"**👩‍🏫 Teacher:** {meta_info.get('Teacher Name', 'N/A')}")
        m2.markdown(f"**🏫 Class:** {meta_info.get('Class', 'N/A')}")
        m3.markdown(f"**📅 Date:** {meta_info.get('Date', 'N/A')}")
        m4.markdown(f"**📝 Assessment:** {meta_info.get('Assessment name', 'N/A')}")
        st.markdown(f"### 📝 Assessment Name: **{meta_info.get('Assessment name', 'N/A')}**")

        raw = pd.read_excel(up_file, header=1)
        obj_names = [c for c in raw.columns if c != 'Student Name']
        mask = raw.iloc[:, 0].astype(str).str.contains("Points for Objectives", case=False, na=False)
        if not mask.any():
            st.error("❌ Need 'Points for Objectives' row."); st.stop()
        max_row = raw[mask].iloc[0]
        obj_max = [float(max_row[c]) if str(max_row.get(c, '')) != '' else 0.0 for c in obj_names]
        student_df = raw[~mask].copy().dropna(subset=['Student Name'])

        def is_absent(row):
            has_A = False
            all_empty = True
            for c in obj_names:
                v = row[c]
                if isinstance(v, str) and 'a' in v.lower():
                    has_A = True
                else:
                    if not (pd.isna(v) or (isinstance(v, str) and v.strip() == '')):
                        all_empty = False
            return has_A or all_empty

        student_df['Absent'] = student_df.apply(is_absent, axis=1)
        for c in obj_names:
            student_df[c] = pd.to_numeric(student_df[c], errors='coerce').fillna(0)

        total_max = sum(obj_max)
        st.info(f"📋 Auto Total Max Mark = **{total_max}**")

        errors = []
        for _, row in student_df.iterrows():
            if row['Absent']: continue
            for j, c in enumerate(obj_names):
                if row[c] > obj_max[j]: errors.append(f"• {row['Student Name']}: {c}={row[c]} > max {obj_max[j]}")
                if row[c] < 0: errors.append(f"• {row['Student Name']}: {c}={row[c]} negative")

        st.subheader("📊 Preview"); st.dataframe(student_df, use_container_width=True)

        if errors:
            st.error("🚫 Fix data entry:\n" + "\n".join(errors))
        else:
            if st.button("Analyze Assessment"):
                res = []
                for _, row in student_df.iterrows():
                    if row['Absent']:
                        res.append({'Student Name': row['Student Name'], 'Total': '-', 'Total %': None, 'Level': 'Absent'})
                        continue
                    ps, tot = [], 0
                    for j, c in enumerate(obj_names):
                        mk = float(row[c]); tot += mk; ps.append((mk / obj_max[j]) * 100 if obj_max[j] else 0)
                    tp = sum(ps) / len(ps)
                    lvl = 'Fail' if tp < 60 else 'Acceptable' if tp < 70 else 'Good' if tp < 80 else 'Very Good' if tp < 90 else 'Outstanding'
                    res.append({'Student Name': row['Student Name'], 'Total': tot, 'Total %': round(tp, 1), 'Level': lvl})
                rdf = pd.DataFrame(res)
                st.header("Step 2: Analysis Report")
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                cnt = rdf['Level'].value_counts().to_dict()
                c1.metric("Absent", cnt.get('Absent', 0)); c2.metric("Fail", cnt.get('Fail', 0)); c3.metric("Acceptable", cnt.get('Acceptable', 0))
                c4.metric("Good", cnt.get('Good', 0)); c5.metric("Very Good", cnt.get('Very Good', 0)); c6.metric("Outstanding", cnt.get('Outstanding', 0))
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
                    st.plotly_chart(px.bar(cdf, x='Level', y='Count', color='Level', category_orders={"Level": ORDER}, color_discrete_map=COLORS), use_container_width=True)
                with v2:
                    fp = px.pie(cdf, names='Level', values='Count', color='Level', color_discrete_map=COLORS, hole=0.3)
                    fp.update_traces(textinfo='percent+label'); st.plotly_chart(fp, use_container_width=True)
                st.dataframe(rdf, use_container_width=True)
                eb = io.BytesIO(); rdf.to_excel(eb, index=False)
                st.download_button("📊 Download Excel", eb.getvalue(), "Report.xlsx")

# ================= TAB 2 =================
with tab2:
    st.header("Compare Multiple Assessments")
    st.info("Choose number of assessments. Upload files (same format as Tab 1). Each score → % before comparing.")
    n_assess = st.number_input("🔢 Number of assessments", min_value=2, max_value=10, value=2, step=1, key="nass")
    files = []
    for i in range(int(n_assess)):
        files.append(st.file_uploader(f"📄 Assessment {i+1}", type=["xlsx", "xls"], key=f"up{i}"))

    if all(files):
        metas = []
        merged = None
        pct_cols = []
        names = []
        for i, f in enumerate(files):
            meta, df = read_meta_and_pct(f)
            if meta is None:
                st.error(f"❌ File {i+1} missing 'Points for Objectives' row."); st.stop()
            metas.append(meta)
            names.append(meta.get('Assessment name', f'Assessment {i+1}'))
            col = f'Pct{i+1}'
            keep = df[['Student Name', 'Pct']].rename(columns={'Pct': col})
            merged = keep if merged is None else pd.merge(merged, keep, on='Student Name', how='outer')
            pct_cols.append(col)

        st.subheader("📋 Assessment Information")
        for i, m in enumerate(metas):
            st.markdown(f"**File {i+1} ({m.get('Assessment name', 'N/A')}):** 👩‍🏫 {m.get('Teacher Name', 'N/A')} | 🏫 {m.get('Class', 'N/A')} | 📅 {m.get('Date', 'N/A')}")
        st.markdown(f"### 📊 Comparing Assessments: **{' / '.join(names)}**")

        merged[pct_cols] = merged[pct_cols].fillna(0)
        merged['Difference'] = (merged[pct_cols[-1]] - merged[pct_cols[0]]).round(1)
        merged['Status'] = merged['Difference'].apply(lambda d: 'Growth' if d > 0.5 else 'Decay' if d < -0.5 else 'Same')

        st.subheader("📊 Comparison Table (Percentage Based)")
        st.dataframe(merged.style.map(color_cell, subset=['Status']), use_container_width=True)

        cnt = merged['Status'].value_counts().to_dict()
        gc, dc, sc = cnt.get('Growth', 0), cnt.get('Decay', 0), cnt.get('Same', 0)
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

        avg = merged[pct_cols].mean().reset_index()
        avg.columns = ['Assessment', 'Average']
        avg['Assessment'] = avg['Assessment'].str.replace('Pct', 'Assess ')
        st.subheader("📈 Average Score Trend (%)")
        st.plotly_chart(px.line(avg, x='Assessment', y='Average', markers=True), use_container_width=True)

        bufc = io.BytesIO(); merged.to_excel(bufc, index=False)
        st.download_button("📊 Download Comparison Excel", bufc.getvalue(), "Comparison.xlsx")

# ================= TAB 3 =================
with tab3:
    st.header("Comparison between Internal and External Assessments")
    st.info("Upload two files. Excel: Row1 Info | Row2 Headers (Student Name, Total) | Row3: 'Total' + max mark (e.g., 40) | Row4+: marks.")
    f1 = st.file_uploader("📄 Internal Assessment", type=["xlsx", "xls"], key="intf")
    f2 = st.file_uploader("📄 External Assessment", type=["xlsx", "xls"], key="extf")

    if f1 and f2:
        m1, df1 = read_internal_external(f1)
        m2, df2 = read_internal_external(f2)
        if m1 is None or m2 is None:
            st.error("❌ One of the files missing 'Total' row/max."); st.stop()

        st.subheader("📋 Assessment Information")
        st.markdown(f"**Internal:** 👩‍🏫 {m1.get('Teacher Name', 'N/A')} | 🏫 {m1.get('Class', 'N/A')} | 📅 {m1.get('Date', 'N/A')} | 📝 {m1.get('Assessment name', 'N/A')}")
        st.markdown(f"**External:** 👩‍🏫 {m2.get('Teacher Name', 'N/A')} | 🏫 {m2.get('Class', 'N/A')} | 📅 {m2.get('Date', 'N/A')} | 📝 {m2.get('Assessment name', 'N/A')}")
        st.markdown(f"### 📊 Comparing: **{m1.get('Assessment name', 'Internal')} / {m2.get('Assessment name', 'External')}**")

        merged = pd.merge(
            df1[['Student Name', 'Pct']].rename(columns={'Pct': 'Pct1'}),
            df2[['Student Name', 'Pct']].rename(columns={'Pct': 'Pct2'}),
            on='Student Name', how='outer'
        ).fillna(0)
        merged['Difference'] = (merged['Pct2'] - merged['Pct1']).round(1)
        merged['Status'] = merged['Difference'].apply(lambda d: 'Growth' if d > 0.5 else 'Decay' if d < -0.5 else 'Same')

        st.subheader("📊 Comparison Table (Percentage Based)")
        st.dataframe(merged.style.map(color_cell, subset=['Status']), use_container_width=True)

        cnt = merged['Status'].value_counts().to_dict()
        gc, dc, sc = cnt.get('Growth', 0), cnt.get('Decay', 0), cnt.get('Same', 0)
        st.subheader("📢 Summary")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("🟩 Growth", gc); mc2.metric("🟥 Decay", dc); mc3.metric("🟨 Same", sc)

        cd = pd.DataFrame({'Status': ['Growth', 'Decay', 'Same'], 'Count': [gc, dc, sc]})
        cd['Status'] = pd.Categorical(cd['Status'], categories=['Decay', 'Same', 'Growth'], ordered=True)
        v1, _ = st.columns([1,1])
        with v1:
            st.markdown("**Bar Chart**")
            st.plotly_chart(px.bar(cd, x='Status', y='Count', color='Status', color_discrete_map={'Growth': 'green', 'Decay': 'red', 'Same': 'yellow'}), use_container_width=True)
        with _:
            st.markdown("**Pie Chart**")
            pf = px.pie(cd, names='Status', values='Count', color='Status', color_discrete_map={'Growth': 'green', 'Decay': 'red', 'Same': 'yellow'}, hole=0.3)
            pf.update_traces(textinfo='percent+label'); st.plotly_chart(pf, use_container_width=True)

        bufc = io.BytesIO(); merged.to_excel(bufc, index=False)
        st.download_button("📊 Download Comparison Excel", bufc.getvalue(), "Internal_External_Comparison.xlsx")
