import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
import os
from fpdf import FPDF

# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="SAIS Analyzer",
    page_icon="📊",
    layout="wide"
)

if os.path.exists("logo.png"):
    try:
        st.image("logo.png", width=120)
    except Exception:
        pass

st.title("📊 SAIS Analyzer")

# ============================================================
# COLORS
# ============================================================

COLORS = {
    "Absent": "#808080",
    "Fail": "#d62728",
    "Acceptable": "#ff7f0e",
    "Good": "#2ca02c",
    "Very Good": "#1f77b4",
    "Outstanding": "#9467bd"
}

ORDER = [
    "Absent",
    "Fail",
    "Acceptable",
    "Good",
    "Very Good",
    "Outstanding"
]

# ============================================================
# TABS
# ============================================================

tab1, tab2 = st.tabs([
    "📊 Single Assessment Analysis",
    "🔄 Comparison (2 Assessments)"
])


# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.header("Step 1: Upload Student Marks Excel")

    st.info(
        "Excel format:\n\n"
        "• Row 1: Teacher Name | Class | Date | Assessment name\n"
        "• Row 2: Student Name | Objective 1 | Objective 2 | Objective 3 | ...\n"
        "• Row 3: Points for Objectives | Maximum | Maximum | Maximum | ...\n"
        "• Row 4+: Student marks"
    )

    up_file = st.file_uploader(
        "Upload Excel",
        type=["xlsx", "xls"],
        key="single"
    )

    if up_file:

        # ====================================================
        # READ ROW 1 - METADATA
        # ====================================================

        up_file.seek(0)

        meta_raw = pd.read_excel(
            up_file,
            nrows=1,
            header=None
        )

        meta_info = {}

        for c in meta_raw.columns:

            value = meta_raw.iloc[0, c]

            if pd.isna(value):
                continue

            value = str(value).strip()

            if ":" in value:
                key, val = value.split(":", 1)
                meta_info[key.strip()] = val.strip()

        # ====================================================
        # DISPLAY INFORMATION
        # ====================================================

        st.subheader("📋 Assessment Information")

        mi1, mi2, mi3, mi4 = st.columns(4)

        mi1.markdown(
            f"**👩‍🏫 Teacher:** "
            f"{meta_info.get('Teacher Name', 'N/A')}"
        )

        mi2.markdown(
            f"**🏫 Class:** "
            f"{meta_info.get('Class', 'N/A')}"
        )

        mi3.markdown(
            f"**📅 Date:** "
            f"{meta_info.get('Date', 'N/A')}"
        )

        mi4.markdown(
            f"**📝 Assessment:** "
            f"{meta_info.get('Assessment name', 'N/A')}"
        )

        # ====================================================
        # READ ROW 2 AS HEADERS
        # ====================================================

        up_file.seek(0)

        raw = pd.read_excel(
            up_file,
            header=1
        )

        raw = raw.dropna(
            axis=1,
            how="all"
        )

        # ====================================================
        # CHECK STUDENT NAME
        # ====================================================

        if "Student Name" not in raw.columns:

            st.error(
                "❌ The first column of Row 2 must be "
                "'Student Name'."
            )

            st.stop()

        # ====================================================
        # OBJECTIVES
        # ====================================================

        obj_names = [
            col
            for col in raw.columns
            if col != "Student Name"
        ]

        if len(obj_names) == 0:

            st.error(
                "❌ No objectives were found."
            )

            st.stop()

        # ====================================================
        # FIND POINTS FOR OBJECTIVES ROW
        # ====================================================

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
                "❌ Row 3 must contain "
                "'Points for Objectives' "
                "in the first column."
            )

            st.stop()

        max_row = raw[mask].iloc[0]

        # ====================================================
        # READ MAXIMUM MARKS
        # ====================================================

        obj_max = []
        max_errors = []

        for col in obj_names:

            value = max_row[col]

            try:

                mx = float(value)

                if mx <= 0:

                    max_errors.append(
                        f"• {col}: maximum mark must be greater than 0."
                    )

            except Exception:

                mx = 0

                max_errors.append(
                    f"• {col}: maximum mark is missing or invalid."
                )

            obj_max.append(mx)

        if max_errors:

            st.error(
                "❌ Problems found in Row 3:\n\n"
                + "\n".join(max_errors)
            )

            st.stop()

        # ====================================================
        # STUDENT DATA
        # ====================================================

        student_df = raw[~mask].copy()

        student_df = student_df.dropna(
            subset=["Student Name"]
        )

        student_df["Student Name"] = (
            student_df["Student Name"]
            .astype(str)
            .str.strip()
        )

        student_df = student_df[
            student_df["Student Name"] != ""
        ]

        # ====================================================
        # CONVERT MARKS TO NUMBERS
        # ====================================================

        for col in obj_names:

            student_df[col] = pd.to_numeric(
                student_df[col],
                errors="coerce"
            )

        # ====================================================
        # VALIDATION
        # ====================================================

        errors = []

        for index, row in student_df.iterrows():

            student_name = row["Student Name"]

            for j, col in enumerate(obj_names):

                value = row[col]
                maximum = obj_max[j]

                # Empty cells are treated as 0
                if pd.isna(value):

                    mark = 0.0

                else:

                    mark = float(value)

                # Check negative marks
                if mark < 0:

                    errors.append(
                        f"• {student_name}: "
                        f"{col} = {mark:g} "
                        f"is negative."
                    )

                # Check marks above maximum
                if mark > maximum:

                    errors.append(
                        f"• {student_name}: "
                        f"{col} = {mark:g} "
                        f"exceeds maximum {maximum:g}."
                    )

        # Replace empty marks with zero
        for col in obj_names:

            student_df[col] = (
                student_df[col]
                .fillna(0)
            )

        # ====================================================
        # TOTAL MAXIMUM
        # ====================================================

        total_max = sum(obj_max)

        st.info(
            f"📋 Total Maximum Mark = "
            f"**{total_max:g}**"
        )

        # ====================================================
        # PREVIEW
        # ====================================================

        st.subheader("📊 Student Data Preview")

        preview_df = student_df[
            ["Student Name"] + obj_names
        ]

        st.dataframe(
            preview_df,
            use_container_width=True
        )

        # ====================================================
        # VALIDATION MESSAGE
        # ====================================================

        analyze_disabled = False

        if errors:

            st.error(
                "🚫 Data entry problems found. "
                "Please fix the Excel file and upload it again.\n\n"
                + "\n".join(errors)
            )

            analyze_disabled = True

        else:

            st.success(
                "✅ No data entry errors found. "
                "You can analyze the assessment."
            )

        # ====================================================
        # ANALYZE
        # ====================================================

        if st.button(
            "🔍 Analyze Assessment",
            disabled=analyze_disabled
        ):

            results = []

            for _, row in student_df.iterrows():

                student_name = row["Student Name"]

                # --------------------------------------------
                # TOTAL OBTAINED
                # --------------------------------------------

                obtained_sum = 0.0

                for col in obj_names:

                    obtained_sum += float(
                        row[col]
                    )

                # --------------------------------------------
                # TOTAL PERCENTAGE
                # --------------------------------------------

                if total_max > 0:

                    total_pct = (
                        obtained_sum /
                        total_max
                    ) * 100

                else:

                    total_pct = 0

                total_pct = round(
                    total_pct,
                    1
                )

                # --------------------------------------------
                # LEVEL
                # --------------------------------------------

                if total_pct < 60:

                    level = "Fail"

                elif total_pct < 70:

                    level = "Acceptable"

                elif total_pct < 80:

                    level = "Good"

                elif total_pct < 90:

                    level = "Very Good"

                else:

                    level = "Outstanding"

                results.append({
                    "Student Name": student_name,
                    "Total": round(
                        obtained_sum,
                        1
                    ),
                    "Total %": total_pct,
                    "Level": level
                })

            # =================================================
            # RESULTS
            # =================================================

            res_df = pd.DataFrame(
                results
            )

            st.header(
                "Step 2: Analysis Report"
            )

            # =================================================
            # LEVEL COUNTS
            # =================================================

            cnt = (
                res_df["Level"]
                .value_counts()
                .to_dict()
            )

            c1, c2, c3, c4, c5, c6 = st.columns(6)

            c1.metric(
                "Absent",
                0
            )

            c2.metric(
                "Fail",
                cnt.get("Fail", 0)
            )

            c3.metric(
                "Acceptable",
                cnt.get("Acceptable", 0)
            )

            c4.metric(
                "Good",
                cnt.get("Good", 0)
            )

            c5.metric(
                "Very Good",
                cnt.get("Very Good", 0)
            )

            c6.metric(
                "Outstanding",
                cnt.get("Outstanding", 0)
            )

            # =================================================
            # OVERALL QUIZ LEVEL
            # =================================================

            st.subheader(
                "📢 Overall Quiz Level"
            )

            total_students = len(
                res_df
            )

            if total_students > 0:

                ge60 = (
                    (
                        res_df["Total %"] >= 60
                    ).sum()
                    / total_students
                    * 100
                )

                gt60 = (
                    (
                        res_df["Total %"] > 60
                    ).sum()
                    / total_students
                    * 100
                )

                gt75 = (
                    (
                        res_df["Total %"] > 75
                    ).sum()
                    / total_students
                    * 100
                )

            else:

                ge60 = 0
                gt60 = 0
                gt75 = 0

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
                f"(Total Maximum = {total_max:g})"
            )

            st.caption(
                f"≥60%: {ge60:.0f}% | "
                f">60%: {gt60:.0f}% | "
                f">75%: {gt75:.0f}%"
            )

            # =================================================
            # VISUALIZATIONS
            # =================================================

            st.subheader(
                "📊 Visualizations"
            )

            cdf = (
                res_df["Level"]
                .value_counts()
                .reindex(
                    ORDER,
                    fill_value=0
                )
                .reset_index()
            )

            cdf.columns = [
                "Level",
                "Count"
            ]

            v1, v2 = st.columns(2)

            # BAR
            with v1:

                st.markdown(
                    "**Bar Chart**"
                )

                fb = px.bar(
                    cdf,
                    x="Level",
                    y="Count",
                    color="Level",
                    category_orders={
                        "Level": ORDER
                    },
                    color_discrete_map=COLORS
                )

                st.plotly_chart(
                    fb,
                    use_container_width=True
                )

            # PIE
            with v2:

                st.markdown(
                    "**Pie Chart**"
                )

                pie_data = cdf[
                    cdf["Count"] > 0
                ]

                fp = px.pie(
                    pie_data,
                    names="Level",
                    values="Count",
                    color="Level",
                    color_discrete_map=COLORS,
                    hole=0.3
                )

                fp.update_traces(
                    textinfo="percent+label"
                )

                st.plotly_chart(
                    fp,
                    use_container_width=True
                )

            # =================================================
            # DETAILED TABLE
            # =================================================

            st.subheader(
                "📋 Detailed Student Table"
            )

            st.dataframe(
                res_df,
                use_container_width=True
            )

            # =================================================
            # EXPORT
            # =================================================

            st.subheader(
                "📥 Export Report"
            )

            e1, e2 = st.columns(2)

            # =================================================
            # EXCEL
            # =================================================

            excel_buffer = io.BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                res_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Analysis Report"
                )

            excel_buffer.seek(0)

            e1.download_button(
                "📊 Download Excel",
                excel_buffer.getvalue(),
                "Assessment_Report.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )

            # =================================================
            # PDF
            # =================================================

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

                teacher = (
                    meta_info
                    .get(
                        "Teacher Name",
                        ""
                    )
                    .encode(
                        "ascii",
                        "ignore"
                    )
                    .decode(
                        "ascii"
                    )
                )

                class_name = (
                    meta_info
                    .get(
                        "Class",
                        ""
                    )
                    .encode(
                        "ascii",
                        "ignore"
                    )
                    .decode(
                        "ascii"
                    )
                )

                date_value = (
                    meta_info
                    .get(
                        "Date",
                        ""
                    )
                    .encode(
                        "ascii",
                        "ignore"
                    )
                    .decode(
                        "ascii"
                    )
                )

                assessment = (
                    meta_info
                    .get(
                        "Assessment name",
                        ""
                    )
                    .encode(
                        "ascii",
                        "ignore"
                    )
                    .decode(
                        "ascii"
                    )
                )

                pdf.cell(
                    0,
                    10,
                    f"Teacher: {teacher}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Class: {class_name}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Date: {date_value}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Assessment: {assessment}",
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
                    f"Total Students: {total_students}",
                    ln=True
                )

                pdf.cell(
                    0,
                    10,
                    f"Total Maximum Mark: {total_max:g}",
                    ln=True
                )

                pdf.ln(5)

                # Charts
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
                        y=75,
                        w=90
                    )

                    pdf.image(
                        io.BytesIO(ip),
                        x=110,
                        y=75,
                        w=90
                    )

                except Exception:
                    pass

                pdf.ln(120)

                # Summary table
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
                        str(r["Level"]),
                        border=1
                    )

                    pdf.cell(
                        40,
                        8,
                        str(r["Count"]),
                        border=1,
                        ln=True
                    )

                pdf_output = pdf.output()

                if isinstance(
                    pdf_output,
                    bytes
                ):

                    pdf_bytes = pdf_output

                else:

                    pdf_bytes = bytes(
                        pdf_output
                    )

                e2.download_button(
                    "📄 Download PDF",
                    pdf_bytes,
                    "Assessment_Report.pdf",
                    mime="application/pdf"
                )

            except Exception as ex:

                e2.error(
                    f"PDF export issue: {ex}"
                )


# ============================================================
# TAB 2 - COMPARISON
# ============================================================

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
                df1.columns[0]: "Student Name"
            }
        )

        df2 = df2.rename(
            columns={
                df2.columns[0]: "Student Name"
            }
        )

        df1[df1.columns[1:]] = (
            df1[df1.columns[1:]]
            .apply(
                pd.to_numeric,
                errors="coerce"
            )
            .fillna(0)
        )

        df2[df2.columns[1:]] = (
            df2[df2.columns[1:]]
            .apply(
                pd.to_numeric,
                errors="coerce"
            )
            .fillna(0)
        )

        df1["Score1"] = (
            df1.drop(
                columns=["Student Name"]
            ).sum(axis=1)
        )

        df2["Score2"] = (
            df2.drop(
                columns=["Student Name"]
            ).sum(axis=1)
        )

        mg = pd.merge(
            df1[
                ["Student Name", "Score1"]
            ],
            df2[
                ["Student Name", "Score2"]
            ],
            on="Student Name"
        )

        mg["Difference"] = (
            mg["Score2"] -
            mg["Score1"]
        ).round(1)

        def stat(d):

            if d > 0.5:
                return "Growth"

            elif d < -0.5:
                return "Decay"

            else:
                return "Same"

        mg["Status"] = (
            mg["Difference"]
            .apply(stat)
        )

        def color_cell(val):

            if val == "Growth":

                return (
                    "background-color: green; "
                    "color: white"
                )

            elif val == "Decay":

                return (
                    "background-color: red; "
                    "color: white"
                )

            elif val == "Same":

                return (
                    "background-color: yellow"
                )

            return ""

        styled = mg.style.map(
            color_cell,
            subset=["Status"]
        )

        st.subheader(
            "📊 Comparison Table (Colored)"
        )

        st.dataframe(
            styled,
            use_container_width=True
        )

        cnt2 = (
            mg["Status"]
            .value_counts()
            .to_dict()
        )

        gc = cnt2.get(
            "Growth",
            0
        )

        dc = cnt2.get(
            "Decay",
            0
        )

        sc = cnt2.get(
            "Same",
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
            "Status": [
                "Growth",
                "Decay",
                "Same"
            ],
            "Count": [
                gc,
                dc,
                sc
            ]
        })

        chart_data["Status"] = pd.Categorical(
            chart_data["Status"],
            categories=[
                "Decay",
                "Same",
                "Growth"
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
                x="Status",
                y="Count",
                color="Status",
                color_discrete_map={
                    "Growth": "green",
                    "Decay": "red",
                    "Same": "yellow"
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
                names="Status",
                values="Count",
                color="Status",
                color_discrete_map={
                    "Growth": "green",
                    "Decay": "red",
                    "Same": "yellow"
                },
                hole=0.3
            )

            pie_fig.update_traces(
                textinfo="percent+label"
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
