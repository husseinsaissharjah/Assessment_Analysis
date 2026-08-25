import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

st.set_page_config(page_title="SAIS Analyzer", page_icon="📊", layout="wide")

if os.path.exists("logo.png"):
    try:
        st.image("logo.png", width=120)
    except Exception:
        pass

st.title("📊 SAIS Analyzer")

COLORS = {'Absent':'#808080','Fail':'#d62728','Acceptable':'#ff7f0e','Good':'#2ca02c','Very Good':'#1f77b4','Outstanding':'#9467bd'}
ORDER = ['Absent','Fail','Acceptable','Good','Very Good','Outstanding']

tab1, tab2 = st.tabs(["📊 Single Assessment Analysis", "🔄 Comparison (Multiple Assessments)"])

# ================= TAB 1 =================
with tab1:
    st.header("Step 1: Upload Student Marks Excel")
    st.info("Row1: Info | Row2: Headers | Row3: 'Points for Objectives' + max marks | Row4+: Marks. Leave empty or put 'A' for absent.")
    up_file = st.file_uploader("Upload Excel", type=["xlsx","xls"], key="single")
    if up_file:
        meta_raw = pd.read_excel(up_file, nrows=1, header=None)
        up_file.seek(0)
        meta_info = {}
        for c in meta_raw.columns:
            val = str(meta_raw.iloc[0,c]).strip()
            if ':' in val:
                k,v = val.split(':',1)
                meta_info[k.strip()] = v.strip()
        st.subheader("📋 Assessment Information")
        m1,m2,m3,m4 = st.columns(4)
        m1.markdown(f"**👩‍🏫 Teacher:** {meta_info.get('Teacher Name','N/A')}")
        m2.markdown(f"**🏫 Class:** {meta_info.get('Class','N/A')}")
        m3.markdown(f"**📅 Date:** {meta_info.get('Date','N/A')}")
        m4.markdown(f"**📝 Assessment:** {meta_info.get('Assessment name','N/A')}")
        
        raw = pd.read_excel(up_file, header=1)
        obj_names = [c for c in raw.columns if c != 'Student Name']
        mask = raw.iloc[:,0].astype(str).str.contains("Points for Objectives", case=False, na=False)
        if not mask.any():
            st.error("❌ Need 'Points for Objectives' row."); st.stop()
        max_row = raw[mask].iloc[0]
        obj_max = [float(max_row[c]) if str(max_row.get(c,''))!='' else 0.0 for c in obj_names]
        student_df = raw[~mask].copy().dropna(subset=['Student Name'])
        
        def is_absent(row):
            has_A = False
            all_empty = True
            for c in obj_names:
                v = row[c]
                if isinstance(v, str) and 'a' in v.lower():
                    has_A = True
                else:
                    if not (pd.isna(v) or (isinstance(v, str) and v.strip()=='')):
                        all_empty = False
            return has_A or all_empty
        
        student_df['Absent'] = student_df.apply(is_absent, axis=1)
        for c in obj_names: 
            student_df[c] = pd.to_numeric(student_df[c], errors='coerce').fillna(0)
        
        total_max = sum(obj_max)
        st.info(f"📋 Auto Total Max Mark = **{total_max}**")
        
        errors = []
        for _,row in student_df.iterrows():
            if row['Absent']: continue
            for j,c in enumerate(obj_names):
                if row[c] > obj_max[j]: errors.append(f"• {row['Student Name']}: {c}={row[c]} > max {obj_max[j]}")
                if row[c] < 0: errors.append(f"• {row['Student Name']}: {c}={row[c]} negative")
        
        st.subheader("📊 Preview"); st.dataframe(student_df, use_container_width=True)
        
        if errors:
            st.error("🚫 Fix data entry:\n"+"\n".join(errors))
        else:
            if st.button("🔍 Analyze Assessment"):
                res = []
                for _,row in student_df.iterrows():
                    if row['Absent']:
                        res.append({'Student Name':row['Student Name'],'Total':'-','Total %':None,'Level':'Absent'})
                        continue
                    ps, tot = [], 0
                    for j,c in enumerate(obj_names):
                        mk = float(row[c]); tot += mk; ps.append((mk/obj_max[j])*100 if obj_max[j] else 0)
                    tp = sum(ps)/len(ps)
                    lvl = 'Fail' if tp<60 else 'Acceptable' if tp<70 else 'Good' if tp<80 else 'Very Good' if tp<90 else 'Outstanding'
                    res.append({'Student Name':row['Student Name'],'Total':tot,'Total %':round(tp,1),'Level':lvl})
                rdf = pd.DataFrame(res)
                
                st.header("Step 2: Analysis Report")
                st.markdown(
                    '<button onclick="window.print()" style="background:#1f77b4;color:white;padding:8px 16px;'
                    'border:none;border-radius:4px;cursor:pointer;font-size:14px;">'
                    '🖨️ Print / Save as PDF</button>',
                    unsafe_allow_html=True
                )
                
                c1,c2,c3,c4,c5,c6 = st.columns(6)
                cnt = rdf['Level'].value_counts().to_dict()
                c1.metric("Absent",cnt.get('Absent',0));c2.metric("Fail",cnt.get('Fail',0));c3.metric("Acceptable",cnt.get('Acceptable',0))
                c4.metric("Good",cnt.get('Good',0));c5.metric("Very Good",cnt.get('Very Good',0));c6.metric("Outstanding",cnt.get('Outstanding',0))
                ts = len(rdf)
                ge60 = (rdf['Total %']>=60).sum()/ts*100 if ts else 0
                gt60 = (rdf['Total %']>60).sum()/ts*100 if ts else 0
                gt75 = (rdf['Total %']>75).sum()/ts*100 if ts else 0
                ov = "Outstanding" if gt75>=90 else "Very Good" if gt60>=90 else "Good" if gt60>=75 else "Acceptable" if ge60>=60 else "Below Acceptable"
                st.success(f"**{ov}** (Max {total_max})")
                cdf = rdf['Level'].value_counts().reset_index(); cdf.columns=['Level','Count']
                cdf['Level']=pd.Categorical(cdf['Level'],categories=ORDER,ordered=True); cdf=cdf.sort_values('Level')
                v1,v2=st.columns(2)
                with v1:
                    fb=px.bar(cdf,x='Level',y='Count',color='Level',category_orders={"Level":ORDER},color_discrete_map=COLORS)
                    st.plotly_chart(fb,use_container_width=True)
                with v2: 
                    fp=px.pie(cdf,names='Level',values='Count',color='Level',color_discrete_map=COLORS,hole=0.3); fp.update_traces(textinfo='percent+label')
                    st.plotly_chart(fp,use_container_width=True)
                st.dataframe(rdf, use_container_width=True)
                
                eb=io.BytesIO(); rdf.to_excel(eb,index=False)
                st.download_button("📊 Download Excel",eb.getvalue(),"Report.xlsx")

# ================= TAB 2 (FIXED PIE CHART) =================
with tab2:
    st.header("Compare Multiple Assessments")
    st.info("Choose number of assessments. Upload files (same format as Tab 1). Each student's score is converted to % (out of 100) before comparing first vs last.")
    n_assess = st.number_input("🔢 Number of assessments", min_value=2, max_value=10, value=2, step=1, key="nass")
    files = []
    for i in range(int(n_assess)):
        files.append(st.file_uploader(f"📄 Assessment {i+1}", type=["xlsx","xls"], key=f"up{i}"))
    
    if all(files):
        merged = None
        for i, f in enumerate(files):
            df = pd.read_excel(f, header=1)
            mask = df.iloc[:,0].astype(str).str.contains("Points for Objectives", case=False, na=False)
            if not mask.any():
                st.error(f"❌ File {i+1} missing 'Points for Objectives' row."); st.stop()
            max_row = df[mask].iloc[0]
            obj_cols = [c for c in df.columns if c != 'Student Name']
            total_max = sum(float(max_row[c]) for c in obj_cols if str(max_row[c]).strip()!='')
            df = df[~mask].copy()
            df = df.rename(columns={df.columns[0]:'Student Name'})
            for c in obj_cols: 
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            df['Obtained'] = df[obj_cols].sum(axis=1)
            df['Pct'] = (df['Obtained'] / total_max * 100).round(1) if total_max else 0.0
            keep = df[['Student Name', 'Pct']].rename(columns={'Pct': f'Pct{i+1}'})
            merged = keep if merged is None else pd.merge(merged, keep, on='Student Name', how='outer')
        
        pct_cols = [f'Pct{i+1}' for i in range(len(files))]
        merged[pct_cols] = merged[pct_cols].fillna(0)
        merged['Difference'] = (merged[pct_cols[-1]] - merged[pct_cols[0]]).round(1)
        merged['Status'] = merged['Difference'].apply(lambda d: 'Growth' if d>0.5 else 'Decay' if d<-0.5 else 'Same')
        
        def color_cell(v):
            if v=='Growth': return 'background-color: green; color: white'
            if v=='Decay': return 'background-color: red; color: white'
            if v=='Same': return 'background-color: yellow'
            return ''
        
        st.subheader("📊 Comparison Table (Percentage Based)")
        st.dataframe(merged.style.map(color_cell, subset=['Status']), use_container_width=True)
        
        cnt = merged['Status'].value_counts().to_dict()
        gc, dc, sc = cnt.get('Growth',0), cnt.get('Decay',0), cnt.get('Same',0)
        st.subheader("📢 Summary")
        m1,m2,m3 = st.columns(3)
        m1.metric("🟩 Growth", gc); m2.metric("🟥 Decay", dc); m3.metric("🟨 Same", sc)
        
        cd = pd.DataFrame({'Status':['Growth','Decay','Same'],'Count':[gc,dc,sc]})
        cd['Status']=pd.Categorical(cd['Status'],categories=['Decay','Same','Growth'],ordered=True)
        v1,v2=st.columns(2)
        with v1:
            st.markdown("**Bar Chart**")
            st.plotly_chart(px.bar(cd,x='Status',y='Count',color='Status',color_discrete_map={'Growth':'green','Decay':'red','Same':'yellow'}), use_container_width=True)
        with v2:
            st.markdown("**Pie Chart**")
            pf=px.pie(cd,names='Status',values='Count',color='Status',color_discrete_map={'Growth':'green','Decay':'red','Same':'yellow'},hole=0.3)
            pf.update_traces(textinfo='percent+label'); st.plotly_chart(pf, use_container_width=True)
        
        avg = merged[pct_cols].mean().reset_index()
        avg.columns = ['Assessment','Average']
        avg['Assessment'] = avg['Assessment'].str.replace('Pct','Assess ')
        st.subheader("📈 Average Score Trend (%)")
        st.plotly_chart(px.line(avg, x='Assessment', y='Average', markers=True), use_container_width=True)
        
        bufc = io.BytesIO(); merged.to_excel(bufc, index=False)
        st.download_button("📊 Download Comparison Excel", bufc.getvalue(), "Comparison.xlsx")
