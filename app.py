import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
from fpdf import FPDF

st.set_page_config(page_title="Assessment Analyzer", layout="wide")
st.title("📊 Student Assessment Analysis Tool")

COLORS = {
    'Absent': '#808080', 'Fail': '#d62728', 'Acceptable': '#ff7f0e',
    'Good': '#2ca02c', 'Very Good': '#1f77b4', 'Outstanding': '#9467bd'
}
ORDER = ['Absent', 'Fail', 'Acceptable', 'Good', 'Very Good', 'Outstanding']

tab1, tab2 = st.tabs(["📊 Single Assessment Analysis", "🔄 Comparison (2 Assessments)"])

# ================= TAB 1: ORIGINAL TOOL =================
with tab1:
    st.header("Step 1: Define Assessment Structure")
    n_obj = st.number_input("🔢 Number of objectives", min_value=1, max_value=30, value=3, step=1, key="n1")
    obj_names, obj_max = [], []
    c1, c2 = st.columns(2)
    for i in range(int(n_obj)):
        with c1:
            nm = st.text_input(f"senior_{i}", value=f"Objective {i+1}", key=f"nm{i}")
        with c2:
            mx = st.number_input(f"Objective {i+1} max mark", min_value=0.0, value=10.0, key=f"mx{i}")
        obj_names.append(nm.strip() if nm.strip() else f"Objective {i+1}")
        obj_max.append(mx)
    total_max = sum(obj_max)
    st.info(f"📋 Auto Total Max Mark = **{total_max}**")

    st.header("Step 2: Upload Student Marks Excel")
    st.info("Excel: First column 'Student Name', then ONE column per objective (actual marks only).")
    up_file = st.file_uploader("Upload Excel", type=["xlsx", "xls"], key="single")

    if up_file:
        df = pd.read_excel(up_file)
        if df.shape[1] < int(n_obj) + 1:
            st.error(f"❌ Excel needs Student Name + {int(n_obj)} marks. Found {df.shape[1]-1}.")
        else:
            df = df.iloc[:, :int(n_obj)+1]
            df.columns = ['Student Name'] + obj_names
            edit_df = df.copy()
            edit_df.insert(1, 'Absent', False)
            st.header("Step 3: Verify / Edit Marks")
            edited = st.data_editor(edit_df, num_rows="fixed", use_container_width=True, key="grid")

            if st.button("🔍 Analyze Assessment"):
                errors = []
                for _, row in edited.iterrows():
                    if row['Absent']:
                        continue
                    for j, obj in enumerate(obj_names):
                        try: mark = float(row[obj]) if str(row[obj]).strip() != '' else 0.0
                        except: mark = 0.0
                        if mark > obj_max[j]:
                            errors.append(f"• {row['Student Name']}: '{obj}' mark = {mark} exceeds max {obj_max[j]}")
                        if mark < 0:
                            errors.append(f"• {row['Student Name']}: '{obj}' mark = {mark} is negative")
                if errors:
                    st.error("🚫 Cannot analyze. Please fix these invalid marks:\n" + "\n".join(errors))
                else:
                    results = []
                    for _, row in edited.iterrows():
                        name = row['Student Name']
                        if row['Absent']:
                            results.append({'Student Name': name, 'Total': '-', 'Total %': None, 'Level': 'Absent'})
                            continue
                        percentages, obtained_sum = [], 0
                        for j, obj in enumerate(obj_names):
                            mark = float(row[obj]) if str(row[obj]).strip() != '' else 0.0
                            mx = obj_max[j] if obj_max[j] != 0 else 1
                            obtained_sum += mark
                            percentages.append((mark/mx)*100)
                        total_pct = sum(percentages)/len(percentages)
                        if total_pct < 60: lvl = 'Fail'
                        elif total_pct < 70: lvl = 'Acceptable'
                        elif total_pct < 80: lvl = 'Good'
                        elif total_pct < 90: lvl = 'Very Good'
                        else: lvl = 'Outstanding'
                        results.append({'Student Name': name, 'Total': obtained_sum, 'Total %': round(total_pct,1), 'Level': lvl})
                    res_df = pd.DataFrame(results)
                    st.header("Step 4: Analysis Report")
                    c1,c2,c3,c4,c5,c6 = st.columns(6)
                    cnt = res_df['Level'].value_counts().to_dict()
                    c1.metric("Absent", cnt.get('Absent',0)); c2.metric("Fail", cnt.get('Fail',0))
                    c3.metric("Acceptable", cnt.get('Acceptable',0)); c4.metric("Good", cnt.get('Good',0))
                    c5.metric("Very Good", cnt.get('Very Good',0)); c6.metric("Outstanding", cnt.get('Outstanding',0))
                    st.subheader("📢 Overall Quiz Level")
                    ts = len(res_df)
                    ge60 = (res_df['Total %']>=60).sum()/ts*100 if ts else 0
                    gt60 = (res_df['Total %']>60).sum()/ts*100 if ts else 0
                    gt75 = (res_df['Total %']>75).sum()/ts*100 if ts else 0
                    if gt75>=90: overall="Outstanding 🌟"
                    elif gt60>=90: overall="Very Good 🏆"
                    elif gt60>=75: overall="Good ✅"
                    elif ge60>=60: overall="Acceptable 🆗"
                    else: overall="Below Acceptable ⚠️"
                    overall_clean = overall.encode('ascii','ignore').decode('ascii').strip()
                    st.success(f"**{overall}** (Out of total max {total_max})")
                    st.caption(f"≥60%: {ge60:.0f}% | >60%: {gt60:.0f}% | >75%: {gt75:.0f}%")
                    st.subheader("📊 Visualizations")
                    cdf = res_df['Level'].value_counts().reset_index()
                    cdf.columns=['Level','Count']
                    cdf['Level']=pd.Categorical(cdf['Level'], categories=ORDER, ordered=True)
                    cdf=cdf.sort_values('Level')
                    v1,v2=st.columns(2)
                    with v1:
                        st.markdown("**Bar Chart**")
                        fb=px.bar(cdf,x='Level',y='Count',color='Level',category_orders={"Level":ORDER},color_discrete_map=COLORS)
                        st.plotly_chart(fb,use_container_width=True)
                    with v2:
                        st.markdown("**Pie Chart**")
                        fp=px.pie(cdf,names='Level',values='Count',color='Level',color_discrete_map=COLORS,hole=0.3)
                        fp.update_traces(textinfo='percent+label')
                        st.plotly_chart(fp,use_container_width=True)
                    st.subheader("Detailed Student Table (with Auto Total)")
                    st.dataframe(res_df, use_container_width=True)
                    st.subheader("📥 Export Report")
                    e1,e2=st.columns(2)
                    e1.download_button("📊 Download Excel", res_df.to_excel(io.BytesIO(),index=False).getvalue(), "Report.xlsx")
                    pdf=FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica","B",16)
                    pdf.cell(0,10,"Assessment Report",ln=True)
                    pdf.set_font("Helvetica","",12)
                    pdf.cell(0,10,f"Overall: {overall_clean}",ln=True)
                    pdf.cell(0,10,f"Total: {ts}",ln=True)
                    pdf.ln(5)
                    ib=pio.to_image(fb,format="png",width=400,height=300)
                    ip=pio.to_image(fp,format="png",width=400,height=300)
                    pdf.image(io.BytesIO(ib),x=10,y=45,w=90)
                    pdf.image(io.BytesIO(ip),x=110,y=45,w=90)
                    pdf.ln(100)
                    pdf.set_font("Helvetica","B",10)
                    pdf.cell(40,8,"Level",border=1)
                    pdf.cell(40,8,"Count",border=1,ln=True)
                    pdf.set_font("Helvetica","",10)
                    for _,r in cdf.iterrows():
                        pdf.cell(40,8,str(r['Level']),border=1)
                        pdf.cell(40,8,str(r['Count']),border=1,ln=True)
                    buf=io.BytesIO()
                    pdf.output(buf)
                    buf.seek(0)
                    e2.download_button("📄 Download PDF", buf.read(), "Report.pdf")

# ================= TAB 2: COMPARISON TOOL (FIXED) =================
with tab2:
    st.header("Upload Two Assessment Files (Same Students)")
    st.info("Excel format: First column 'Student Name', remaining columns are mark columns. The app sums the marks for each student and compares Assessment 1 vs Assessment 2.")
    
    f1 = st.file_uploader("📄 Assessment 1 Excel", type=["xlsx","xls"], key="f1")
    f2 = st.file_uploader("📄 Assessment 2 Excel", type=["xlsx","xls"], key="f2")

    if f1 and f2:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        df1 = df1.rename(columns={df1.columns[0]: 'Student Name'})
        df2 = df2.rename(columns={df2.columns[0]: 'Student Name'})
        
        df1[df1.columns[1:]] = df1[df1.columns[1:]].apply(pd.to_numeric, errors='coerce').fillna(0)
        df2[df2.columns[1:]] = df2[df2.columns[1:]].apply(pd.to_numeric, errors='coerce').fillna(0)
        
        df1['Score1'] = df1.drop(columns=['Student Name']).sum(axis=1)
        df2['Score2'] = df2.drop(columns=['Student Name']).sum(axis=1)
        
        mg = pd.merge(df1[['Student Name', 'Score1']], df2[['Student Name', 'Score2']], on='Student Name')
        mg['Difference'] = (mg['Score2'] - mg['Score1']).round(1)
        
        def stat(d):
            if d > 0.5: return 'Growth'
            elif d < -0.5: return 'Decay'
            else: return 'Same'
        mg['Status'] = mg['Difference'].apply(stat)
        
        def color_cell(val):
            if val == 'Growth': return 'background-color: green; color: white'
            elif val == 'Decay': return 'background-color: red; color: white'
            elif val == 'Same': return 'background-color: yellow'
            return ''
        styled = mg.style.map(color_cell, subset=['Status'])
        
        st.subheader("📊 Comparison Table (Colored)")
        st.dataframe(styled, use_container_width=True)
        
        cnt2 = mg['Status'].value_counts().to_dict()
        gc = cnt2.get('Growth', 0)
        dc = cnt2.get('Decay', 0)
        sc = cnt2.get('Same', 0)
        
        st.subheader("📢 Comparison Summary")
        m1,m2,m3 = st.columns(3)
        m1.metric("🟩 Growth", gc)
        m2.metric("🟥 Decay", dc)
        m3.metric("🟨 Same", sc)
        
        chart_data = pd.DataFrame({
            'Status': ['Growth', 'Decay', 'Same'],
            'Count': [gc, dc, sc]
        })
        chart_data['Status'] = pd.Categorical(chart_data['Status'], categories=['Decay','Same','Growth'], ordered=True)
        
        st.subheader("📊 Visualizations")
        v1, v2 = st.columns(2)
        with v1:
            st.markdown("**Bar Chart – Progress Counts**")
            bar_fig = px.bar(chart_data, x='Status', y='Count', color='Status',
                             color_discrete_map={'Growth':'green', 'Decay':'red', 'Same':'yellow'})
            st.plotly_chart(bar_fig, use_container_width=True)
        with v2:
            st.markdown("**Pie Chart – Progress Distribution**")
            pie_fig = px.pie(chart_data, names='Status', values='Count',
                             color='Status', color_discrete_map={'Growth':'green', 'Decay':'red', 'Same':'yellow'}, hole=0.3)
            pie_fig.update_traces(textinfo='percent+label')
            st.plotly_chart(pie_fig, use_container_width=True)
            
        bufc = io.BytesIO()
        mg.to_excel(bufc, index=False)
        st.download_button("📊 Download Comparison Excel", bufc.getvalue(), "Comparison.xlsx")