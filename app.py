import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SAIS Analyzer",
    page_icon="📊",
    layout="wide"
)

COLORS = {
    'Absent': '#808080',
    'Fail': '#d62728',
    'Acceptable': '#ff7f0e',
    'Good': '#2ca02c',
    'Very Good': '#1f77b4',
    'Outstanding': '#9467bd'
}

ORDER = [
    'Absent',
    'Fail',
    'Acceptable',
    'Good',
    'Very Good',
    'Outstanding'
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def color_cell(v):
    if v == 'Growth':
        return 'background-color: green; color: white'
    if v == 'Decay':
        return 'background-color: red; color: white'
    if v == 'Same':
        return 'background-color: yellow'
    return ''


# =========================================================
# EXCEL TEMPLATE FUNCTIONS
# =========================================================

def objectives_template():

    data = [
        [
            "Teacher Name: Example Teacher",
            "Class: Grade 7A",
            "Date: 27/08/2026",
            "Assessment name: Quiz 1",
            "Subject: Mathematics"
        ],
        [
            "Student Name",
            "Objective 1",
            "Objective 2",
            "Objective 3",
            ""
        ],
        [
            "Points for Objectives",
            10,
            15,
            5,
            ""
        ],
        [
            "Student 1",
            8,
            12,
            4,
            ""
        ],
        [
            "Student 2",
            10,
            14,
            5,
            ""
        ],
        [
            "Student 3",
            "A",
            "A",
            "A",
            ""
        ]
    ]

    df = pd.DataFrame(data)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            header=False,
            sheet_name="Assessment"
        )

    buffer.seek(0)

    return buffer.getvalue()


def total_template():

    data = [
        [
            "Teacher Name: Example Teacher",
            "Class: Grade 7A",
            "Date: 27/08/2026",
            "Assessment name: Internal Assessment",
            "Subject: Mathematics"
        ],
        [
            "Student Name",
            "Total"
        ],
        [
            "Total",
            100
        ],
        [
            "Student 1",
            82
        ],
        [
            "Student 2",
            91
        ],
        [
            "Student 3",
            65
        ]
    ]

    df = pd.DataFrame(data)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            header=False,
            sheet_name="Assessment"
        )

    buffer.seek(0)

    return buffer.getvalue()


def map_template():

    data = {
        "Student Name": [
            "Student 1",
            "Student 2",
            "Student 3",
            "Student 4"
        ],
        "Grade": [
            7,
            7,
            7,
            7
        ],
        "Subject": [
            "Mathematics",
            "Mathematics",
            "Mathematics",
            "Mathematics"
        ],
        "Previous RIT": [
            205,
            210,
            198,
            215
        ],
        "Current RIT": [
            210,
            214,
            200,
            218
        ],
        "Percentile": [
            55,
            70,
            40,
            85
        ]
    }

    df = pd.DataFrame(data)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="MAP Data"
        )

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# OBJECTIVES FILE READER
# =========================================================

def read_objectives_file(f):

    meta_raw = pd.read_excel(
        f,
        nrows=1,
        header=None
    )

    f.seek(0)

    meta = {}

    for c in meta_raw.columns:

        val = str(meta_raw.iloc[0, c]).strip()

        if ':' in val:

            k, v = val.split(':', 1)

            meta[k.strip()] = v.strip()

    df = pd.read_excel(
        f,
        header=1
    )

    mask = df.iloc[:, 0].astype(str).str.contains(
        "Points for Objectives",
        case=False,
        na=False
    )

    if not mask.any():
        return None, None

    max_row = df[mask].iloc[0]

    raw_obj_cols = [
        c for c in df.columns
        if c != 'Student Name'
    ]

    valid_cols = []

    total_max = 0.0

    for c in raw_obj_cols:

        hdr = str(c).strip()

        mx_raw = max_row[c]

        mx_str = str(mx_raw).strip()

        if (
            hdr != ''
            and hdr.lower() != 'nan'
            and not hdr.startswith('Unnamed')
            and mx_str != ''
            and mx_str.lower() != 'nan'
        ):

            try:
                mx = float(mx_raw)

            except:
                mx = 0.0

            if mx > 0:

                valid_cols.append(c)

                total_max += mx

    obj_cols = valid_cols

    df = df[~mask].copy()

    df = df.rename(
        columns={
            df.columns[0]: 'Student Name'
        }
    )

    if obj_cols:

        df = df[
            ['Student Name'] + obj_cols
        ]

    for c in obj_cols:

        df[c] = pd.to_numeric(
            df[c],
            errors='coerce'
        ).fillna(0)

    df['Obtained'] = (
        df[obj_cols].sum(axis=1)
        if obj_cols
        else 0
    )

    df['Pct'] = (
        df['Obtained'] / total_max * 100
    ).round(1) if total_max else 0.0

    return meta, df


# =========================================================
# TOTAL FILE READER
# =========================================================

def read_total_file(f):

    raw = pd.read_excel(
        f,
        header=None
    )

    meta = {}

    for c in raw.iloc[0, :]:

        val = str(c).strip()

        if ':' in val:

            k, v = val.split(':', 1)

            meta[k.strip()] = v.strip()

    headers = [
        str(x).strip()
        for x in raw.iloc[1, :].tolist()
    ]

    total_idx = None

    for i in range(2, len(raw)):

        if 'total' in str(raw.iloc[i, 0]).lower():

            total_idx = i

            break

    if total_idx is None:
        return None, None

    try:

        max_total = float(
            raw.iloc[total_idx, 1]
        )

    except:

        max_total = 100.0

    data = raw.iloc[2:, :].copy()

    data.columns = headers

    data = data[
        data.iloc[:, 0]
        .astype(str)
        .str.lower()
        .str.contains('total')
        == False
    ]

    data = data.rename(
        columns={
            data.columns[0]: 'Student Name'
        }
    )

    total_col = [
        c for c in data.columns
        if 'total' in str(c).lower()
    ]

    if not total_col:
        return None, None

    total_col = total_col[0]

    data[total_col] = pd.to_numeric(
        data[total_col],
        errors='coerce'
    ).fillna(0)

    data['Pct'] = (
        data[total_col] / max_total * 100
    ).round(1) if max_total else 0.0

    return meta, data


# =========================================================
# SIDEBAR
# =========================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📊 Overview",
        "👨‍🎓 Student Analysis",
        "📚 Grade Analysis",
        "📈 MAP Analysis",
        "🎯 Achievement & Gaps",
        "📑 Reports"
    ]
)


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    if os.path.exists("logo.png"):

        st.image(
            "logo.png",
            width=120
        )

    st.title("SAIS Analyzer")

    st.markdown(
        "### Student Assessment & Achievement Dashboard"
    )

    st.markdown(
        "Analyze MAP, internal assessments, grades, "
        "and student performance in seconds."
    )

    st.markdown("---")

    st.markdown("### 📌 How to use")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            "### ① Upload Data\n"
            "Upload your Excel files with student marks."
        )

    with c2:

        st.markdown(
            "### ② Choose Analysis\n"
            "Pick the analysis type from the sidebar."
        )

    with c3:

        st.markdown(
            "### ③ View Insights\n"
            "See charts, gaps, and download reports."
        )

    st.info(
        "Use the sidebar on the left "
        "to navigate to your analysis."
    )


# =========================================================
# OVERVIEW
# =========================================================

elif page == "📊 Overview":

    st.title("📊 SAIS Analyzer Overview")

    st.markdown(
        """
        The SAIS Analyzer is designed to help teachers,
        coordinators, and school leaders analyze student
        achievement quickly and consistently.
        """
    )

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.subheader("👨‍🎓 Student Analysis")

        st.write(
            """
            Analyze one assessment at a time using learning
            objectives and student marks.
            """
        )

        st.markdown(
            """
            **This service helps you:**
            - Calculate student totals and percentages.
            - Identify absent students.
            - Classify student achievement levels.
            - View bar and pie charts.
            - Download the final analysis as Excel.
            """
        )

    with c2:

        st.subheader("📚 Grade Analysis")

        st.write(
            """
            Compare multiple assessments for the same group
            of students and monitor their academic progress.
            """
        )

        st.markdown(
            """
            **This service helps you:**
            - Compare assessment results.
            - Convert scores to percentages.
            - Identify student growth.
            - Identify student decay.
            - Identify students with stable performance.
            - View grade performance trends.
            """
        )

    with c3:

        st.subheader("🎯 Achievement & Gaps")

        st.write(
            """
            Compare Internal Assessment results with External
            Assessment results to identify achievement gaps.
            """
        )

        st.markdown(
            """
            **This service helps you:**
            - Compare Internal vs External results.
            - Identify performance gaps.
            - Identify Growth, Decay, and Same performance.
            - Support intervention planning.
            - Download comparison reports.
            """
        )

    st.markdown("---")

    st.subheader("📈 MAP Analysis")

    st.markdown(
        """
        The MAP Analysis service helps analyze student
        performance using MAP Growth RIT scores.
        """
    )

    st.info(
        """
        **What is a RIT Score?**

        A RIT score is the scale used in MAP Growth to measure
        a student's academic achievement and instructional level.

        Unlike a percentage or a score out of 100, the RIT scale
        is an equal-interval scale. This allows educators to monitor
        measurable academic growth over time.

        For example, a student moving from a RIT score of 200 to
        210 has demonstrated growth on the MAP scale.
        """
    )

    st.markdown(
        """
        **MAP Analysis can help identify:**

        - 📊 Current student achievement.
        - 📈 Growth between testing periods.
        - 🎯 Student percentile.
        - 👥 Students requiring intervention.
        - 🌟 Students requiring enrichment.
        - 📚 Overall grade performance.
        """
    )


# =========================================================
# STUDENT ANALYSIS
# =========================================================

elif page == "👨‍🎓 Student Analysis":

    st.header("👨‍🎓 Student Analysis")

    st.markdown(
        """
        Analyze a single assessment based on learning
        objectives and student marks.
        """
    )

    st.download_button(
        "📥 Download Excel Template",
        objectives_template(),
        "Student_Analysis_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    st.header("Step 1: Upload Student Marks Excel")

    st.info(
        """
        Row 1: Assessment Information

        Row 2: Headers

        Row 3: 'Points for Objectives' + Maximum Marks

        Row 4+: Student Marks

        Leave empty or enter 'A' for absent students.
        """
    )

    up_file = st.file_uploader(
        "Upload Excel",
        type=["xlsx", "xls"],
        key="single"
    )

    if up_file:

        meta_raw = pd.read_excel(
            up_file,
            nrows=1,
            header=None
        )

        up_file.seek(0)

        meta_info = {}

        for c in meta_raw.columns:

            val = str(
                meta_raw.iloc[0, c]
            ).strip()

            if ':' in val:

                k, v = val.split(':', 1)

                meta_info[
                    k.strip()
                ] = v.strip()

        st.subheader("📋 Info")

        m1, m2, m3, m4 = st.columns(4)

        m1.markdown(
            f"**👩‍🏫 Teacher:** "
            f"{meta_info.get('Teacher Name', 'N/A')}"
        )

        m2.markdown(
            f"**🏫 Class:** "
            f"{meta_info.get('Class', 'N/A')}"
        )

        m3.markdown(
            f"**📅 Date:** "
            f"{meta_info.get('Date', 'N/A')}"
        )

        m4.markdown(
            f"**📝 Assessment:** "
            f"{meta_info.get('Assessment name', 'N/A')}"
        )

        st.markdown(
            f"### 📝 Name: "
            f"**{meta_info.get('Assessment name', 'N/A')}** "
            f"| 📚 Subject: "
            f"**{meta_info.get('Subject', 'N/A')}**"
        )

        raw = pd.read_excel(
            up_file,
            header=1
        )

        all_obj_names = [
            c for c in raw.columns
            if c != 'Student Name'
        ]

        mask = (
            raw.iloc[:, 0]
            .astype(str)
            .str.contains(
                "Points for Objectives",
                case=False,
                na=False
            )
        )

        if not mask.any():

            st.error(
                "❌ Need 'Points for Objectives' row."
            )

            st.stop()

        max_row = raw[mask].iloc[0]

        obj_names = []

        obj_max = []

        for c in all_obj_names:

            hdr = str(c).strip()

            mx_raw = max_row[c]

            mx_str = str(mx_raw).strip()

            if (
                hdr != ''
                and hdr.lower() != 'nan'
                and not hdr.startswith('Unnamed')
                and mx_str != ''
                and mx_str.lower() != 'nan'
            ):

                try:

                    mx = float(mx_raw)

                except:

                    mx = 0.0

                if mx > 0:

                    obj_names.append(c)

                    obj_max.append(mx)

        student_df = (
            raw[~mask]
            .copy()
            .dropna(subset=['Student Name'])
        )

        student_df = student_df[
            ['Student Name'] + obj_names
        ].copy()

        def is_absent(row):

            has_A = False

            all_empty = True

            for c in obj_names:

                v = row[c]

                if (
                    isinstance(v, str)
                    and 'a' in v.lower()
                ):

                    has_A = True

                elif not (
                    pd.isna(v)
                    or (
                        isinstance(v, str)
                        and v.strip() == ''
                    )
                ):

                    all_empty = False

            return has_A or all_empty

        student_df['Absent'] = student_df.apply(
            is_absent,
            axis=1
        )

        for c in obj_names:

            student_df[c] = pd.to_numeric(
                student_df[c],
                errors='coerce'
            ).fillna(0)

        total_max = sum(obj_max)

        st.info(
            f"📋 Auto Total Max Mark = "
            f"**{total_max}**"
        )

        errors = []

        for _, row in student_df.iterrows():

            if row['Absent']:
                continue

            for j, c in enumerate(obj_names):

                if row[c] > obj_max[j]:

                    errors.append(
                        f"• {row['Student Name']}: "
                        f"{c}={row[c]} > max {obj_max[j]}"
                    )

                if row[c] < 0:

                    errors.append(
                        f"• {row['Student Name']}: "
                        f"{c}={row[c]} negative"
                    )

        st.subheader("📊 Preview")

        st.dataframe(
            student_df,
            use_container_width=True
        )

        if errors:

            st.error(
                "🚫 Fix data entry:\n"
                + "\n".join(errors)
            )

        else:

            if st.button(
                "Analyze Assessment"
            ):

                res = []

                for _, row in student_df.iterrows():

                    if row['Absent']:

                        res.append(
                            {
                                'Student Name':
                                    row['Student Name'],
                                'Total': '-',
                                'Total %': None,
                                'Level': 'Absent'
                            }
                        )

                        continue

                    ps = []

                    tot = 0

                    for j, c in enumerate(obj_names):

                        mk = float(row[c])

                        tot += mk

                        ps.append(
                            (mk / obj_max[j]) * 100
                            if obj_max[j]
                            else 0
                        )

                    tp = sum(ps) / len(ps)

                    lvl = (
                        'Fail'
                        if tp < 60
                        else 'Acceptable'
                        if tp < 70
                        else 'Good'
                        if tp < 80
                        else 'Very Good'
                        if tp < 90
                        else 'Outstanding'
                    )

                    res.append(
                        {
                            'Student Name':
                                row['Student Name'],
                            'Total':
                                tot,
                            'Total %':
                                round(tp, 1),
                            'Level':
                                lvl
                        }
                    )

                rdf = pd.DataFrame(res)

                st.header(
                    "Step 2: Analysis Report"
                )

                c1, c2, c3, c4, c5, c6 = st.columns(6)

                cnt = (
                    rdf['Level']
                    .value_counts()
                    .to_dict()
                )

                c1.metric(
                    "Absent",
                    cnt.get('Absent', 0)
                )

                c2.metric(
                    "Fail",
                    cnt.get('Fail', 0)
                )

                c3.metric(
                    "Acceptable",
                    cnt.get('Acceptable', 0)
                )

                c4.metric(
                    "Good",
                    cnt.get('Good', 0)
                )

                c5.metric(
                    "Very Good",
                    cnt.get('Very Good', 0)
                )

                c6.metric(
                    "Outstanding",
                    cnt.get('Outstanding', 0)
                )

                ts = len(rdf)

                ge60 = (
                    (rdf['Total %'] >= 60).sum()
                    / ts
                    * 100
                    if ts
                    else 0
                )

                gt60 = (
                    (rdf['Total %'] > 60).sum()
                    / ts
                    * 100
                    if ts
                    else 0
                )

                gt75 = (
                    (rdf['Total %'] > 75).sum()
                    / ts
                    * 100
                    if ts
                    else 0
                )

                ov = (
                    "Outstanding"
                    if gt75 >= 90
                    else "Very Good"
                    if gt60 >= 90
                    else "Good"
                    if gt60 >= 75
                    else "Acceptable"
                    if ge60 >= 60
                    else "Below Acceptable"
                )

                st.success(
                    f"**{ov}** "
                    f"(Max {total_max})"
                )

                cdf = (
                    rdf['Level']
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

                cdf = cdf.sort_values(
                    'Level'
                )

                v1, v2 = st.columns(2)

                with v1:

                    st.plotly_chart(
                        px.bar(
                            cdf,
                            x='Level',
                            y='Count',
                            color='Level',
                            category_orders={
                                "Level": ORDER
                            },
                            color_discrete_map=COLORS
                        ),
                        use_container_width=True
                    )

                with v2:

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

                st.dataframe(
                    rdf,
                    use_container_width=True
                )

                eb = io.BytesIO()

                rdf.to_excel(
                    eb,
                    index=False
                )

                st.download_button(
                    "📊 Download Excel",
                    eb.getvalue(),
                    "Report.xlsx"
                )


# =========================================================
# GRADE ANALYSIS
# =========================================================

elif page == "📚 Grade Analysis":

    st.header(
        "📚 Compare Multiple Assessments"
    )

    st.download_button(
        "📥 Download Excel Template",
        objectives_template(),
        "Grade_Analysis_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.info(
        """
        Choose the number of assessments.

        Upload files using the same Excel format as
        Student Analysis.

        Each assessment score will automatically be converted
        to a percentage before comparison.
        """
    )

    n_assess = st.number_input(
        "🔢 Number of assessments",
        min_value=2,
        max_value=10,
        value=2,
        step=1,
        key="nass"
    )

    files = []

    for i in range(int(n_assess)):

        files.append(
            st.file_uploader(
                f"📄 Assessment {i + 1}",
                type=["xlsx", "xls"],
                key=f"up{i}"
            )
        )

    if all(files):

        metas = []

        merged = None

        pct_cols = []

        names = []

        for i, f in enumerate(files):

            meta, df = read_objectives_file(f)

            if meta is None:

                st.error(
                    f"❌ File {i + 1} missing "
                    "'Points for Objectives' row."
                )

                st.stop()

            metas.append(meta)

            names.append(
                meta.get(
                    'Assessment name',
                    f'Assessment {i + 1}'
                )
            )

            col = f'Pct{i + 1}'

            keep = (
                df[
                    ['Student Name', 'Pct']
                ]
                .rename(
                    columns={'Pct': col}
                )
            )

            merged = (
                keep
                if merged is None
                else pd.merge(
                    merged,
                    keep,
                    on='Student Name',
                    how='outer'
                )
            )

            pct_cols.append(col)

        st.subheader(
            "📋 Assessment Information"
        )

        for i, m in enumerate(metas):

            st.markdown(
                f"**File {i + 1} "
                f"({m.get('Assessment name', 'N/A')}):** "
                f"👩‍🏫 {m.get('Teacher Name', 'N/A')} "
                f"| 🏫 {m.get('Class', 'N/A')} "
                f"| 📅 {m.get('Date', 'N/A')} "
                f"| 📚 {m.get('Subject', 'N/A')}"
            )

        st.markdown(
            f"### 📊 Comparing: "
            f"**{' / '.join(names)}** "
            f"| 📚 Subject: "
            f"**{metas[0].get('Subject', 'N/A')}**"
        )

        merged[pct_cols] = (
            merged[pct_cols]
            .fillna(0)
        )

        merged['Difference'] = (
            merged[pct_cols[-1]]
            - merged[pct_cols[0]]
        ).round(1)

        merged['Status'] = (
            merged['Difference']
            .apply(
                lambda d:
                'Growth'
                if d > 0.5
                else 'Decay'
                if d < -0.5
                else 'Same'
            )
        )

        st.subheader(
            "📊 Comparison Table "
            "(Percentage Based)"
        )

        st.dataframe(
            merged.style.map(
                color_cell,
                subset=['Status']
            ),
            use_container_width=True
        )

        cnt = (
            merged['Status']
            .value_counts()
            .to_dict()
        )

        gc = cnt.get(
            'Growth',
            0
        )

        dc = cnt.get(
            'Decay',
            0
        )

        sc = cnt.get(
            'Same',
            0
        )

        st.subheader("📢 Summary")

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

        cd = pd.DataFrame(
            {
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
            }
        )

        cd['Status'] = pd.Categorical(
            cd['Status'],
            categories=[
                'Decay',
                'Same',
                'Growth'
            ],
            ordered=True
        )

        v1, v2 = st.columns(2)

        with v1:

            st.markdown(
                "**Bar Chart**"
            )

            st.plotly_chart(
                px.bar(
                    cd,
                    x='Status',
                    y='Count',
                    color='Status',
                    color_discrete_map={
                        'Growth': 'green',
                        'Decay': 'red',
                        'Same': 'yellow'
                    }
                ),
                use_container_width=True
            )

        with v2:

            st.markdown(
                "**Pie Chart**"
            )

            pf = px.pie(
                cd,
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

            pf.update_traces(
                textinfo='percent+label'
            )

            st.plotly_chart(
                pf,
                use_container_width=True
            )

        avg = (
            merged[pct_cols]
            .mean()
            .reset_index()
        )

        avg.columns = [
            'Assessment',
            'Average'
        ]

        avg['Assessment'] = (
            avg['Assessment']
            .str.replace(
                'Pct',
                'Assess '
            )
        )

        st.subheader(
            "📈 Average Score Trend (%)"
        )

        st.plotly_chart(
            px.line(
                avg,
                x='Assessment',
                y='Average',
                markers=True
            ),
            use_container_width=True
        )

        bufc = io.BytesIO()

        merged.to_excel(
            bufc,
            index=False
        )

        st.download_button(
            "📊 Download Comparison Excel",
            bufc.getvalue(),
            "Comparison.xlsx"
        )


# =========================================================
# MAP ANALYSIS
# =========================================================

elif page == "📈 MAP Analysis":

    st.title("📈 MAP Analysis")

    st.info(
        """
        ### What is a RIT Score?

        The RIT score is the scale used by MAP Growth to measure
        student achievement and instructional level.

        A RIT score is not a percentage and it is not a score out
        of 100.

        The scale is designed to measure academic growth over time.
        For example, a student moving from 205 to 212 has shown
        measurable growth of 7 RIT points.
        """
    )

    st.markdown(
        """
        ### What this analysis does

        - Calculates RIT growth.
        - Identifies Growth, Decay, or Same performance.
        - Shows student percentile.
        - Calculates grade average RIT.
        - Identifies students below the selected percentile.
        - Identifies students requiring intervention or enrichment.
        """
    )

    st.download_button(
        "📥 Download MAP Excel Template",
        map_template(),
        "MAP_Analysis_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    map_file = st.file_uploader(
        "📄 Upload MAP Data Excel",
        type=["xlsx", "xls"],
        key="map"
    )

    if map_file:

        try:

            map_df = pd.read_excel(
                map_file
            )

            required_cols = [
                "Student Name",
                "Grade",
                "Subject",
                "Previous RIT",
                "Current RIT",
                "Percentile"
            ]

            missing = [
                c for c in required_cols
                if c not in map_df.columns
            ]

            if missing:

                st.error(
                    "❌ Missing columns: "
                    + ", ".join(missing)
                )

                st.stop()

            map_df[
                "Previous RIT"
            ] = pd.to_numeric(
                map_df["Previous RIT"],
                errors="coerce"
            )

            map_df[
                "Current RIT"
            ] = pd.to_numeric(
                map_df["Current RIT"],
                errors="coerce"
            )

            map_df[
                "Percentile"
            ] = pd.to_numeric(
                map_df["Percentile"],
                errors="coerce"
            )

            map_df["RIT Growth"] = (
                map_df["Current RIT"]
                - map_df["Previous RIT"]
            )

            map_df["Growth Status"] = (
                map_df["RIT Growth"]
                .apply(
                    lambda x:
                    "Growth"
                    if x > 0
                    else "Decay"
                    if x < 0
                    else "Same"
                )
            )

            map_df["Support Level"] = (
                map_df["Percentile"]
                .apply(
                    lambda x:
                    "Intervention"
                    if x < 25
                    else "Monitor"
                    if x < 50
                    else "On Track"
                    if x < 75
                    else "Enrichment"
                )
            )

            st.subheader(
                "📋 MAP Data Preview"
            )

            st.dataframe(
                map_df,
                use_container_width=True
            )

            st.markdown("---")

            st.subheader(
                "📊 MAP Summary"
            )

            total_students = len(map_df)

            avg_previous = (
                map_df[
                    "Previous RIT"
                ].mean()
            )

            avg_current = (
                map_df[
                    "Current RIT"
                ].mean()
            )

            avg_growth = (
                map_df[
                    "RIT Growth"
                ].mean()
            )

            avg_percentile = (
                map_df[
                    "Percentile"
                ].mean()
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "👥 Students",
                total_students
            )

            c2.metric(
                "📉 Previous Avg RIT",
                round(avg_previous, 1)
            )

            c3.metric(
                "📈 Current Avg RIT",
                round(avg_current, 1)
            )

            c4.metric(
                "🚀 Average Growth",
                round(avg_growth, 1)
            )

            st.metric(
                "🎯 Average Percentile",
                round(avg_percentile, 1)
            )

            st.markdown("---")

            status_count = (
                map_df[
                    "Growth Status"
                ]
                .value_counts()
                .reset_index()
            )

            status_count.columns = [
                "Status",
                "Count"
            ]

            v1, v2 = st.columns(2)

            with v1:

                st.subheader(
                    "📈 Student Growth"
                )

                st.plotly_chart(
                    px.bar(
                        map_df,
                        x="Student Name",
                        y="RIT Growth",
                        color="Growth Status"
                    ),
                    use_container_width=True
                )

            with v2:

                st.subheader(
                    "📊 Growth Distribution"
                )

                st.plotly_chart(
                    px.pie(
                        status_count,
                        names="Status",
                        values="Count",
                        hole=0.3
                    ),
                    use_container_width=True
                )

            st.markdown("---")

            st.subheader(
                "🎯 Student Percentile"
            )

            st.plotly_chart(
                px.bar(
                    map_df,
                    x="Student Name",
                    y="Percentile",
                    color="Support Level",
                    range_y=[0, 100]
                ),
                use_container_width=True
            )

            st.subheader(
                "👥 Support Groups"
            )

            support_count = (
                map_df[
                    "Support Level"
                ]
                .value_counts()
                .reset_index()
            )

            support_count.columns = [
                "Support Level",
                "Students"
            ]

            st.dataframe(
                support_count,
                use_container_width=True
            )

            st.subheader(
                "📋 Student MAP Analysis"
            )

            st.dataframe(
                map_df.style.map(
                    color_cell,
                    subset=["Growth Status"]
                ),
                use_container_width=True
            )

            map_buffer = io.BytesIO()

            map_df.to_excel(
                map_buffer,
                index=False
            )

            st.download_button(
                "📥 Download MAP Analysis",
                map_buffer.getvalue(),
                "MAP_Analysis_Report.xlsx"
            )

        except Exception as e:

            st.error(
                f"❌ Error reading MAP file: {e}"
            )


# =========================================================
# ACHIEVEMENT & GAPS
# =========================================================

elif page == "🎯 Achievement & Gaps":

    st.header(
        "🎯 Comparison between Internal and External Assessments"
    )

    st.download_button(
        "📥 Download Excel Template",
        total_template(),
        "Achievement_Gaps_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.info(
        """
        Upload two files.

        Excel Format:

        Row 1: Assessment Information

        Row 2: Headers
        (Student Name, Total)

        Row 3:
        'Total' + Maximum Mark

        Row 4+:
        Student Marks
        """
    )

    f1 = st.file_uploader(
        "📄 Internal Assessment",
        type=["xlsx", "xls"],
        key="intf"
    )

    f2 = st.file_uploader(
        "📄 External Assessment",
        type=["xlsx", "xls"],
        key="extf"
    )

    if f1 and f2:

        m1, df1 = read_total_file(f1)

        m2, df2 = read_total_file(f2)

        if m1 is None or m2 is None:

            st.error(
                "❌ One of the files "
                "is missing the 'Total' row/max."
            )

            st.stop()

        st.subheader(
            "📋 Assessment Information"
        )

        st.markdown(
            f"**Internal:** "
            f"👩‍🏫 {m1.get('Teacher Name', 'N/A')} "
            f"| 🏫 {m1.get('Class', 'N/A')} "
            f"| 📅 {m1.get('Date', 'N/A')} "
            f"| 📝 {m1.get('Assessment name', 'N/A')} "
            f"| 📚 {m1.get('Subject', 'N/A')}"
        )

        st.markdown(
            f"**External:** "
            f"👩‍🏫 {m2.get('Teacher Name', 'N/A')} "
            f"| 🏫 {m2.get('Class', 'N/A')} "
            f"| 📅 {m2.get('Date', 'N/A')} "
            f"| 📝 {m2.get('Assessment name', 'N/A')} "
            f"| 📚 {m2.get('Subject', 'N/A')}"
        )

        st.markdown(
            f"### 📊 Comparing: "
            f"**{m1.get('Assessment name', 'Internal')} "
            f"/ "
            f"{m2.get('Assessment name', 'External')}** "
            f"| 📚 Subject: "
            f"**{m1.get('Subject', 'N/A')}**"
        )

        merged = pd.merge(

            df1[
                ['Student Name', 'Pct']
            ].rename(
                columns={'Pct': 'Pct1'}
            ),

            df2[
                ['Student Name', 'Pct']
            ].rename(
                columns={'Pct': 'Pct2'}
            ),

            on='Student Name',

            how='outer'

        ).fillna(0)

        merged['Difference'] = (
            merged['Pct2']
            - merged['Pct1']
        ).round(1)

        merged['Status'] = (
            merged['Difference']
            .apply(
                lambda d:
                'Growth'
                if d > 0.5
                else 'Decay'
                if d < -0.5
                else 'Same'
            )
        )

        st.subheader(
            "📊 Comparison Table "
            "(Percentage Based)"
        )

        st.dataframe(
            merged.style.map(
                color_cell,
                subset=['Status']
            ),
            use_container_width=True
        )

        cnt = (
            merged['Status']
            .value_counts()
            .to_dict()
        )

        gc = cnt.get(
            'Growth',
            0
        )

        dc = cnt.get(
            'Decay',
            0
        )

        sc = cnt.get(
            'Same',
            0
        )

        st.subheader("📢 Summary")

        mc1, mc2, mc3 = st.columns(3)

        mc1.metric(
            "🟩 Growth",
            gc
        )

        mc2.metric(
            "🟥 Decay",
            dc
        )

        mc3.metric(
            "🟨 Same",
            sc
        )

        cd = pd.DataFrame(
            {
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
            }
        )

        cd['Status'] = pd.Categorical(
            cd['Status'],
            categories=[
                'Decay',
                'Same',
                'Growth'
            ],
            ordered=True
        )

        v1, v2 = st.columns(2)

        with v1:

            st.markdown(
                "**Bar Chart**"
            )

            st.plotly_chart(
                px.bar(
                    cd,
                    x='Status',
                    y='Count',
                    color='Status',
                    color_discrete_map={
                        'Growth': 'green',
                        'Decay': 'red',
                        'Same': 'yellow'
                    }
                ),
                use_container_width=True
            )

        with v2:

            st.markdown(
                "**Pie Chart**"
            )

            pf = px.pie(
                cd,
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

            pf.update_traces(
                textinfo='percent+label'
            )

            st.plotly_chart(
                pf,
                use_container_width=True
            )

        bufc = io.BytesIO()

        merged.to_excel(
            bufc,
            index=False
        )

        st.download_button(
            "📊 Download Comparison Excel",
            bufc.getvalue(),
            "Internal_External_Comparison.xlsx"
        )


# =========================================================
# REPORTS
# =========================================================

elif page == "📑 Reports":

    st.title("📑 Reports")

    st.info(
        """
        Reports generated from each analysis can be downloaded
        directly from the relevant analysis page.

        Future versions can include:

        • School-level reports

        • Grade-level reports

        • Class comparison

        • MAP vs Internal Assessment comparison

        • Automatic PDF reports
        """
    )
