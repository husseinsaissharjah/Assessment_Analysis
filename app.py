import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
import os
from fpdf import FPDF

st.set_page_config(page_title="SAIS Analyzer", page_icon="📊", layout="wide")

if os.path.exists("logo.png"):
    try:
        st.image("logo.png", width=120)
    except Exception:
        pass

st.title("📊 SAIS Analyzer")

COLORS = {
    'Absent': '#808080', 'Fail': '#d62728', 'Acceptable': '#ff7f0e',
    'Good': '#2ca02c', 'Very Good': '#1f77b4', 'Outstanding': '#9467bd'
}
ORDER = ['Absent', 'Fail', 'Acceptable', 'Good', 'Very Good', 'Outstanding']

tab1, tab2 = st.tabs(["📊 Single Assessment Analysis", "🔄 Comparison (2 Assessments)"])

# ================= TAB 1 =================
with tab1:
    st.header("Step 1: Upload Student Marks Excel")
    st.info(
        "Excel format:\n"
        "• Row 1: Info (Teacher Name: X, Class: Y, Date: Z, Assessment name: W)\n"
        "• Row 2: Headers (Student Name, Objective 1, Objective 2, ...)\n"
        "• Row 3: First cell = 'Points for Objectives', then the MAX mark for each objective\n"
        "• Row 4+: Student marks"
    )

    up_file = st.file_uploader("Upload Excel", type=["xlsx", "xls"], key="single")

    if up_file:

        # ----------------------------------------------------
        # READ ROW 1 - METADATA
        # ----------------------------------------------------
        meta_raw = pd.read_excel(up_file, nrows=1, header=None)

        up_file.seek(0)

        meta_info = {}

        for c in meta_raw.columns:
            val = str(meta_raw.iloc[0, c]).strip()

            if ':' in val:
                k, v = val.split(':', 1)
                meta_info[k.strip()] = v.strip()

        st.subheader("📋 Assessment Information")

        mi1, mi2, mi3, mi4 = st.columns(4)

        mi1.markdown(
            f"**👩‍🏫 Teacher:** {meta_info.get('Teacher Name', 'N/A')}"
        )

        mi2.markdown(
            f"**🏫 Class:** {meta_info.get('Class', 'N/A')}"
        )

        mi3.markdown(
            f"**📅 Date:** {meta_info.get('Date', 'N/A')}"
        )

        mi4.markdown(
            f"**📝 Assessment:** {meta_info.get('Assessment name', 'N/A')}"
        )

        # ----------------------------------------------------
        # READ ROW 2 AS HEADERS
        # ----------------------------------------------------
        raw = pd.read_excel(up_file, header=1)

        # Remove completely empty columns
        raw = raw.dropna(axis=1, how='all')

        if 'Student Name' not in raw.columns:
            st.error(
                "❌ Row 2 must contain 'Student Name' "
                "as the first column."
            )
            st.stop()

        obj_names = [
            col for col in raw.columns
            if col != 'Student Name'
        ]

        # ----------------------------------------------------
        # FIND ROW 3 - POINTS FOR OBJECTIVES
        # ----------------------------------------------------
        mask = (
            raw.iloc[:, 0]
            .astype(str)
            .str.strip()
            .str.contains(
                "Points for Objectives",
                case=False,
                na=False
            )
        )

        if not mask.any():
            st.error(
                "❌ Row 3 must have 'Points for Objectives' "
                "in the first column with max marks next to it."
            )
            st.stop()

        # Get the Points for Objectives row
        max_row = raw[mask].iloc[0]

        # ----------------------------------------------------
        # GET MAXIMUM MARK FOR EACH OBJECTIVE
        # ----------------------------------------------------
        obj_max = []

        for col in obj_names:
            try:
                mx = float(max_row[col])
            except:
                mx = 0.0

            obj_max.append(mx)

        # ----------------------------------------------------
        # REMOVE THE POINTS FOR OBJECTIVES ROW
        # FROM STUDENT DATA
        # ----------------------------------------------------
        student_df = raw[~mask].copy()

        # Remove empty student rows
        student_df = student_df.dropna(
            subset=['Student Name']
        )

        # Convert objective marks to numbers
        for col in obj_names:
            student_df[col] = pd.to_numeric(
                student_df[col],
                errors='coerce'
            ).fillna(0)

        # ----------------------------------------------------
        # TOTAL MAXIMUM
        # ----------------------------------------------------
        total_max = sum(obj_max)

        st.info(
            f"📋 Auto Total Max Mark = **{total_max}** "
            f"(from Excel)"
        )

        # ----------------------------------------------------
        # VALIDATE ON UPLOAD
        # ----------------------------------------------------
        errors = []

        for _, row in student_df.iterrows():

            for j, col in enumerate(obj_names):

                mark = row[col]
                mx = obj_max[j]

                if mark > mx:
                    errors.append(
                        f"• {row['Student Name']}: "
                        f"'{col}' mark = {mark} "
                        f"exceeds max {mx}"
                    )

                if mark < 0:
                    errors.append(
                        f"• {row['Student Name']}: "
                        f"'{col}' mark = {mark} "
                        f"is negative"
                    )

        # ----------------------------------------------------
        # STUDENT DATA PREVIEW
        # ----------------------------------------------------
        st.subheader("📊 Student Data Preview")

        st.dataframe(
            student_df,
            use_container_width=True
        )

        analyze_disabled = False

        if errors:

            st.error(
                "🚫 Data entry problems found. "
                "Please fix in Excel and re-upload:\n"
                + "\n".join(errors)
            )

            analyze_disabled = True

        else:

            st.success(
                "✅ No data entry errors found. "
                "You can analyze!"
            )

        # ----------------------------------------------------
        # ORIGINAL ANALYSIS - UNCHANGED
        # ----------------------------------------------------
        if st.button(
            "🔍 Analyze Assessment",
            disabled=analyze_disabled
        ):

            results = []

            for _, row in student_df.iterrows():

                name = row['Student Name']

                percentages = []
                obtained_sum = 0

                for j, col in enumerate(obj_names):

                    mark = float(row[col])

                    mx = (
                        obj_max[j]
                        if obj_max[j] != 0
                        else 1
                    )

                    obtained_sum += mark

                    percentages.append(
                        (mark / mx) * 100
                    )

                total_pct = (
                    sum(percentages)
                    / len(percentages)
                )

                if total_pct < 60:
                    lvl = 'Fail'

                elif total_pct < 70:
                    lvl = 'Acceptable'

                elif total_pct < 80:
                    lvl = 'Good'

                elif total_pct < 90:
                    lvl = 'Very Good'

                else:
                    lvl = 'Outstanding'

                results.append({
                    'Student Name': name,
                    'Total': obtained_sum,
                    'Total %': round(total_pct, 1),
                    'Level': lvl
                })

            res_df = pd.DataFrame(results)

            st.header("Step 2: Analysis Report")

            c1, c2, c3, c4, c5, c6 = st.columns(6)

            cnt = res_df['Level'].value_counts().to_dict()

            c1.metric("Absent", 0)
            c2.metric("Fail", cnt.get('Fail', 0))
            c3.metric("Acceptable", cnt.get('Acceptable', 0))
            c4.metric("Good", cnt.get('Good', 0))
            c5.metric("Very Good", cnt.get('Very Good', 0))
            c6.metric("Outstanding", cnt.get('Outstanding', 0))

            # ------------------------------------------------
            # ORIGINAL OVERALL QUIZ LEVEL
            # ------------------------------------------------
            st.subheader("📢 Overall Quiz Level")

            ts = len(res_df)

            ge60 = (
                (res_df['Total %'] >= 60).sum()
                / ts * 100
                if ts else 0
            )

            gt60 = (
                (res_df['Total %'] > 60).sum()
                / ts * 100
                if ts else 0
            )

            gt75 = (
                (res_df['Total %'] > 75).sum()
                / ts * 100
                if ts else 0
            )

            if gt75 >= 90:
                overall = "Outstanding"

            elif gt60 >= 90:
                overall = "Very Good"

            elif gt60 >= 75:
                overall = "Good"

            elif ge60 >= 60:
                overall = "Acceptable"

            else:
                overall = "Below Acceptable"

            st.success(
                f"**{overall}** "
                f"(Out of total max {total_max})"
            )

            st.caption(
                f"≥60%: {ge60:.0f}% | "
                f">60%: {gt60:.0f}% | "
                f">75%: {gt75:.0f}%"
            )

            # ------------------------------------------------
            # ORIGINAL VISUALIZATIONS
            # ------------------------------------------------
            st.subheader("📊 Visualizations")

            cdf = (
                res_df['Level']
                .value_counts()
                .reset_index()
            )

            cdf.columns = [
                'Level',
                'Count'
            ]

            cdf['Level'] = pd.Categorical(
                cdf['Level'],
                categories=ORDER,
                ordered=True
            )

            cdf = cdf.sort_values('Level')

            v1, v2 = st.columns(2)

            with v1:

                st.markdown("**Bar Chart**")

                fb = px.bar(
                    cdf,
                    x='Level',
                    y='Count',
                    color='Level',
                    category_orders={
                        "Level": ORDER
                    },
                    color_discrete_map=COLORS
                )

                st.plotly_chart(
                    fb,
                    use_container_width=True
                )

            with v2:

                st.markdown("**Pie Chart**")

                fp = px.pie(
                    cdf,
                    names='Level',
                    values='Count',
                    color='Level',
                    color_discrete_map=COLORS,
                    hole=0.3
                )

                fp.update_traces(
                    textinfo='percent+label'
                )

                st.plotly_chart(
                    fp,
                    use_container_width=True
                )

            # ------------------------------------------------
            # ORIGINAL DETAILED TABLE
            # ------------------------------------------------
            st.subheader(
                "Detailed Student Table (with Auto Total)"
            )

            st.dataframe(
                res_df,
                use_container_width=True
            )

            # ------------------------------------------------
            # ORIGINAL EXPORT REPORT
            # ------------------------------------------------
            st.subheader("📥 Export Report")

            e1, e2 = st.columns(2)

            excel_buffer = io.BytesIO()

            res_df.to_excel(
                excel_buffer,
                index=False
            )

            e1.download_button(
                "📊 Download Excel",
                excel_buffer.getvalue(),
                "Report.xlsx"
            )

            try:

                pdf = FPDF()

                pdf.add_page()

                pdf.set_font(
                    "Helvetica",
                    "B",
                    16
                )

                pdf.cell(
                    0,
                    10,
                    "Assessment Report",
                    ln=True
                )

                pdf.set_font(
                    "Helvetica",
                    "",
                    12
                )

                tn = (
                    meta_info
                    .get('Teacher Name', '')
                    .encode('ascii', 'ignore')
                    .decode('ascii')
                )

                cl = (
                    meta_info
                    .get('Class', '')
                    .encode('ascii', 'ignore')
                    .decode('ascii')
                )

                dt = (
                    meta_info
                    .get('Date', '')
                    .encode('ascii', 'ignore')
                    .decode('ascii')
                )

                an = (
                    meta_info
                    .get('Assessment name', '')
                    .encode('ascii', 'ignore')
                    .decode('ascii')
                )

                pdf.cell(
                    0,
                    10,
                    f"Teacher: {tn}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Class: {cl}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Date: {dt}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Assessment: {an}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Overall: {overall}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Total Students: {ts}",
                    ln=True
                )

                pdf.ln(5)

                try:

                    ib = pio.to_image(
                        fb,
                        format="png",
                        width=400,
                        height=300
                    )

                    ip = pio.to_image(
                        fp,
                        format="png",
                        width=400,
                        height=300
                    )

                    pdf.image(
                        io.BytesIO(ib),
                        x=10,
                        y=70,
                        w=90
                    )

                    pdf.image(
                        io.BytesIO(ip),
                        x=110,
                        y=70,
                        w=90
                    )

                except Exception:
                    pass

                pdf.ln(120)

                pdf.set_font(
                    "Helvetica",
                    "B",
                    10
                )

                pdf.cell(
                    40,
                    8,
                    "Level",
                    border=1
                )

                pdf.cell(
                    40,
                    8,
                    "Count",
                    border=1,
                    ln=True
                )

                pdf.set_font(
                    "Helvetica",
                    "",
                    10
                )

                for _, r in cdf.iterrows():

                    pdf.cell(
                        40,
                        8,
                        str(r['Level']),
                        border=1
                    )

                    pdf.cell(
                        40,
                        8,
                        str(r['Count']),
                        border=1,
                        ln=True
                    )

                buf = io.BytesIO()

                pdf.output(buf)

                buf.seek(0)

                e2.download_button(
                    "📄 Download PDF",
                    buf.read(),
                    "Report.pdf"
                )

            except Exception as ex:

                e2.error(
                    f"PDF export issue: {ex}"
                )


# ================= TAB 2 (UNCHANGED) =================
with tab2:

    st.header(
        "Upload Two Assessment Files (Same Students)"
    )

    st.info(
        "Excel format: First column 'Student Name', "
        "remaining columns are mark columns. "
        "The app sums the marks for each student "
        "and compares Assessment 1 vs Assessment 2."
    )

    f1 = st.file_uploader(
        "📄 Assessment 1 Excel",
        type=["xlsx", "xls"],
        key="f1"
    )

    f2 = st.file_uploader(
        "📄 Assessment 2 Excel",
        type=["xlsx", "xls"],
        key="f2"
    )

    if f1 and f2:

        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)

        df1 = df1.rename(
            columns={
                df1.columns[0]: 'Student Name'
            }
        )

        df2 = df2.rename(
            columns={
                df2.columns[0]: 'Student Name'
            }
        )

        df1[df1.columns[1:]] = (
            df1[df1.columns[1:]]
            .apply(
                pd.to_numeric,
                errors='coerce'
            )
            .fillna(0)
        )

        df2[df2.columns[1:]] = (
            df2[df2.columns[1:]]
            .apply(
                pd.to_numeric,
                errors='coerce'
            )
            .fillna(0)
        )

        df1['Score1'] = (
            df1.drop(
                columns=['Student Name']
            ).sum(axis=1)
        )

        df2['Score2'] = (
            df2.drop(
                columns=['Student Name']
            ).sum(axis=1)
        )

        mg = pd.merge(
            df1[['Student Name', 'Score1']],
            df2[['Student Name', 'Score2']],
            on='Student Name'
        )

        mg['Difference'] = (
            mg['Score2'] -
            mg['Score1']
        ).round(1)

        def stat(d):

            if d > 0.5:
                return 'Growth'

            elif d < -0.5:
                return 'Decay'

            else:
                return 'Same'

        mg['Status'] = (
            mg['Difference']
            .apply(stat)
        )

        def color_cell(val):

            if val == 'Growth':
                return (
                    'background-color: green; '
                    'color: white'
                )

            elif val == 'Decay':
                return (
                    'background-color: red; '
                    'color: white'
                )

            elif val == 'Same':
                return (
                    'background-color: yellow'
                )

            return ''

        styled = mg.style.map(
            color_cell,
            subset=['Status']
        )

        st.subheader(
            "📊 Comparison Table (Colored)"
        )

        st.dataframe(
            styled,
            use_container_width=True
        )

        cnt2 = (
            mg['Status']
            .value_counts()
            .to_dict()
        )

        gc = cnt2.get(
            'Growth',
            0
        )

        dc = cnt2.get(
            'Decay',
            0
        )

        sc = cnt2.get(
            'Same',
            0
        )

        st.subheader(
            "📢 Comparison Summary"
        )

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "🟩 Growth",
            gc
        )

        m2.metric(
            "🟥 Decay",
            dc
        )

        m3.metric(
            "🟨 Same",
            sc
        )

        chart_data = pd.DataFrame({
            'Status': [
                'Growth',
                'Decay',
                'Same'
            ],
            'Count': [
                gc,
                dc,
                sc
            ]
        })

        chart_data['Status'] = pd.Categorical(
            chart_data['Status'],
            categories=[
                'Decay',
                'Same',
                'Growth'
            ],
            ordered=True
        )

        st.subheader(
            "📊 Visualizations"
        )

        v1, v2 = st.columns(2)

        with v1:

            st.markdown(
                "**Bar Chart – Progress Counts**"
            )

            bar_fig = px.bar(
                chart_data,
                x='Status',
                y='Count',
                color='Status',
                color_discrete_map={
                    'Growth': 'green',
                    'Decay': 'red',
                    'Same': 'yellow'
                }
            )

            st.plotly_chart(
                bar_fig,
                use_container_width=True
            )

        with v2:

            st.markdown(
                "**Pie Chart – Progress Distribution**"
            )

            pie_fig = px.pie(
                chart_data,
                names='Status',
                values='Count',
                color='Status',
                color_discrete_map={
                    'Growth': 'green',
                    'Decay': 'red',
                    'Same': 'yellow'
                },
                hole=0.3
            )

            pie_fig.update_traces(
                textinfo='percent+label'
            )

            st.plotly_chart(
                pie_fig,
                use_container_width=True
            )

        bufc = io.BytesIO()

        mg.to_excel(
            bufc,
            index=False
        )

        st.download_button(
            "📊 Download Comparison Excel",
            bufc.getvalue(),
            "Comparison.xlsx"
        )
