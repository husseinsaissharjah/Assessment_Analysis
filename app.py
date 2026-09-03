import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Assessment Analysis",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

if "lang" not in st.session_state:
    st.session_state.lang = "English"

# =========================================================
# TRANSLATIONS
# =========================================================
TRANSLATIONS = {
    "Arabic": {
        # Navigation
        "Navigation": "التنقل",
        "🏠 Home": "🏠 الرئيسية",
        "📊 Overview": "📊 نظرة عامة",
        "📝 Objective Analysis": "📝 تحليل الأهداف",
        "📈 Class Total Average Analysis": "📈 تحليل متوسط الصف",
        "🗺️ MAP Analysis": "🗺️ تحليل MAP",
        "🎯 Achievement & Gaps": "🎯 الإنجاز والفجوات",
        "📑 Reports": "📑 التقارير",

        # Home
        "Assessment Analysis": "تحليل التقييم",
        "Student Assessment & Achievement Dashboard": "لوحة تقييم الطلاب والإنجاز",
        "Analyze MAP, internal assessments, grades, and student performance in seconds.":
            "حلل نتائج MAP والتقييمات الداخلية والدرجات وأداء الطلاب خلال ثوانٍ.",
        "📌 How to use": "📌 كيفية الاستخدام",
        "① Upload Data": "① تحميل البيانات",
        "Upload your Excel files with student marks.": "قم بتحميل ملفات Excel التي تحتوي على علامات الطلاب.",
        "② Choose Analysis": "② اختر نوع التحليل",
        "Pick the analysis type from the sidebar.": "اختر نوع التحليل من القائمة الجانبية.",
        "③ View Insights": "③ عرض النتائج",
        "See charts, gaps, and download reports.": "شاهد الرسوم البيانية والفجوات وقم بتحميل التقارير.",
        "Use the sidebar on the left to navigate to your analysis.": "استخدم القائمة الجانبية للتنقل بين أقسام التحليل.",

        # Overview
        "📊 Assessment Analysis Overview": "📊 نظرة عامة على تحليل التقييم",
        "The Assessment Analysis tool is designed to help teachers, coordinators, and school leaders analyze student achievement quickly and consistently.":
            "صُممت أداة تحليل التقييم لمساعدة المعلمين والمنسقين وقادة المدارس على تحليل إنجاز الطلاب بسرعة وبطريقة متسقة.",
        "Analyze one assessment at a time using learning objectives and student marks.":
            "حلل تقييماً واحداً في كل مرة باستخدام أهداف التعلم وعلامات الطلاب.",
        "Compare multiple assessments for the same class and monitor the class average progress over time.":
            "قارن بين عدة تقييمات للصف نفسه وتابع تطور متوسط الصف مع مرور الوقت.",
        "Compare Internal Assessment results with MAP Percentile in one sheet to identify achievement gaps.":
            "قارن نتائج التقييم الداخلي مع النسبة المئوية لـ MAP في ورقة واحدة لتحديد فجوات الإنجاز.",
        "The MAP Analysis section allows you to compare previous and current RIT scores, growth, and percentile performance.":
            "يسمح قسم تحليل MAP بمقارنة درجات RIT السابقة والحالية، والنمو، وأداء النسبة المئوية.",

        # General
        "👩‍🏫 Teacher:": "👩‍🏫 المعلم:",
        "🏫 Class:": "🏫 الصف:",
        "📅 Date:": "📅 التاريخ:",
        "📝 Assessment:": "📝 التقييم:",
        "📚 Subject:": "📚 المادة:",
        "Name:": "الاسم:",
        "Subject:": "المادة:",
        "Class": "الصف",
        "Class:": "الصف:",
        "Info": "معلومات",
        "📋 Info": "📋 معلومات",
        "📋 Assessment Information": "📋 معلومات التقييم",
        "Assessment": "التقييم",

        # Attendance
        "Total Students": "إجمالي الطلاب",
        "Present / Assessed": "الحاضرون / تم تقييمهم",
        "Absent Students": "الطلاب الغائبون",
        "Absent %": "نسبة الغياب",
        "of total students": "من إجمالي الطلاب",

        # Levels
        "Absent": "غائب",
        "Fail": "راسب",
        "Acceptable": "مقبول",
        "Good": "جيد",
        "Very Good": "جيد جداً",
        "Outstanding": "متميز",

        # Growth
        "Growth": "نمو",
        "Decay": "تراجع",
        "Same": "ثابت",

        # Support
        "Intervention": "تدخل",
        "Monitor": "مراقبة",
        "On Track": "على المسار",
        "Enrichment": "إثراء",
        "N/A": "غير متوفر",
        "Support Level": "مستوى الدعم",

        # Bands
        "Below 60% (Weak)": "أقل من 60% (ضعيف)",
        "60-75% (Acceptable)": "60-75% (مقبول)",
        "76-85% (Very Good)": "76-85% (جيد جداً)",
        "86-100% (Excellent)": "86-100% (ممتاز)",
        "Below Acceptable": "أقل من المقبول",

        # Objective Analysis
        "Objective Analysis": "تحليل الأهداف",
        "Analyze a single assessment based on learning objectives and student marks.":
            "حلل تقييماً واحداً بناءً على أهداف التعلم وعلامات الطلاب.",
        "Auto Total Max Mark": "إجمالي الدرجة القصوى تلقائياً",
        "Objectives": "الأهداف",
        "Preview": "معاينة",
        "Analyze Assessment": "تحليل التقييم",
        "Step 1: Upload Student Marks Excel": "الخطوة 1: تحميل ملف Excel لعلامات الطلاب",
        "Step 2: Analysis Report": "الخطوة 2: تقرير التحليل",
        "📊 Comparison Table (Percentage Based)": "📊 جدول المقارنة (حسب النسبة المئوية)",
        "📢 Summary": "📢 الملخص",
        "Bar Chart": "الرسم البياني الشريطي",
        "Pie Chart": "الرسم البياني الدائري",
        "📈 Average Score Trend (%)": "📈 اتجاه متوسط الدرجات (%)",
        "📈 Student Growth (Difference)": "📈 نمو الطالب (الفرق)",
        "👥 Support Groups": "👥 مجموعات الدعم",
        "🎯 Student Support Levels": "🎯 مستويات دعم الطلاب",
        "📊 Student Achievement": "📊 إنجاز الطلاب",
        "📊 Level Distribution": "📊 توزيع المستويات",

        # Upload / Download
        "Upload Excel": "تحميل Excel",
        "📥 Download Excel Template": "📥 تحميل قالب Excel",
        "📊 Download Excel": "📊 تحميل Excel",
        "📊 Download Comparison Excel": "📊 تحميل Excel المقارنة",

        # MAP
        "🗺️ MAP Analysis": "🗺️ تحليل MAP",
        "📄 Upload MAP Data Excel": "📄 تحميل ملف Excel لبيانات MAP",
        "📥 Download MAP Excel Template": "📥 تحميل قالب Excel لـ MAP",
        "📋 MAP Data Preview": "📋 معاينة بيانات MAP",
        "📊 MAP Summary": "📊 ملخص MAP",
        "👥 Students": "👥 الطلاب",
        "📉 Previous Avg RIT": "📉 متوسط RIT السابق",
        "📈 Current Avg RIT": "📈 متوسط RIT الحالي",
        "🚀 Average Growth": "🚀 متوسط النمو",
        "🎯 Average Percentile": "🎯 متوسط النسبة المئوية",
        "📈 Student Growth": "📈 نمو الطلاب",
        "📊 Growth Distribution": "📊 توزيع النمو",
        "📋 Student MAP Analysis": "📋 تحليل MAP للطلاب",
        "📥 Download MAP Analysis": "📥 تحميل تحليل MAP",
        "Growth Distribution": "توزيع النمو",
        "🎯 Student Percentile": "🎯 النسبة المئوية للطلاب",
        "What is a RIT Score?": "ما هي درجة RIT؟",
        "The RIT score is the scale used by MAP Growth to measure student achievement.":
            "درجة RIT هي المقياس الذي يستخدمه MAP Growth لقياس إنجاز الطالب الأكاديمي.",

        # Achievement & Gaps
        "🎯 Achievement & Gaps (Internal vs MAP)": "🎯 الإنجاز والفجوات (التقييم الداخلي مقابل MAP)",
        "📄 Upload Single Sheet": "📄 تحميل ورقة واحدة",
        "Status": "الحالة",
        "Count": "العدد",
        "Students": "الطلاب",
        "📈 Student Gap (Difference)": "📈 فجوة الطالب (الفرق)",

        # Reports
        "Select Service": "اختر الخدمة",
        "Compare between sections": "مقارنة بين الأقسام",
        "🔍 Compare Between Sections": "🔍 مقارنة بين الأقسام",
        "Comparison Type": "نوع المقارنة",
        "By Assessment Objectives": "حسب أهداف التقييم",
        "By Assessment Total Mark": "حسب الدرجة الإجمالية للتقييم",
        "By External Benchmark Assessment": "حسب تقييم المعيار الخارجي",
        "📚 By Assessment Objectives": "📚 حسب أهداف التقييم",
        "Number of classes": "عدد الفصول",
        "📄 Class": "📄 الصف",
        "file": "ملف",
        "📊 Band Distribution per Class": "📊 توزيع الفئات لكل صف",
        "Band": "الفئة",
        "Student Count": "عدد الطلاب",
        "Performance Band": "فئة الأداء",
        "Student Growth": "نمو الطلاب",
        "🏆 Class Order per Objective (Rank 1 = Highest Average %)":
            "🏆 ترتيب الصفوف حسب الهدف (المرتبة 1 = أعلى متوسط %)",
        "Dumbbell Chart (Class gap per Band)": "مخطط الفروق بين الصفوف حسب الفئة",
        "Available Services": "الخدمات المتاحة",
        "📚 Objectives:": "📚 الأهداف:",
        "Max": "الحد الأقصى",
        "Score": "الدرجة",

        # Errors
        "❌ Need 'Points for Objectives' row.": "❌ يجب أن يحتوي الملف على صف 'Points for Objectives'.",
        "🚫 Fix data entry:": "🚫 يرجى تصحيح إدخال البيانات:",
        "❌ File missing 'Points for Objectives' row.": "❌ الملف يفتقد صف 'Points for Objectives'.",
        "❌ File missing required rows/columns.": "❌ الملف يفتقد الصفوف أو الأعمدة المطلوبة.",
        "❌ Missing columns: ": "❌ الأعمدة المفقودة: ",
        "❌ Error reading MAP file: ": "❌ خطأ في قراءة ملف MAP: ",
        "❌ Class file invalid": "❌ ملف الصف غير صالح",

        # Instructions
        ("Row 1: Assessment Information\n"
         "Row 2: Headers (Objective names)\n"
         "Row 3: Objective Descriptions\n"
         "Row 4: 'Points for Objectives' + Maximum Marks\n"
         "Row 5+: Student Marks\n"
         "Leave empty or enter 'A' for absent students."):
            ("الصف 1: معلومات التقييم\n"
             "الصف 2: العناوين (أسماء الأهداف)\n"
             "الصف 3: وصف الأهداف\n"
             "الصف 4: 'Points for Objectives' + الدرجات القصوى\n"
             "الصف 5 وما بعده: علامات الطلاب\n"
             "اترك الخانة فارغة أو أدخل 'A' للطالب الغائب."),

        "Choose the number of assessments. Upload files using the same Excel format as Objective Analysis.":
            "اختر عدد التقييمات. قم بتحميل الملفات باستخدام نفس تنسيق Excel المستخدم في تحليل الأهداف.",
        "🔢 Number of assessments": "🔢 عدد التقييمات",
    }
}

# =========================================================
# TRANSLATION FUNCTION
# =========================================================
def t(text):
    if st.session_state.lang == "Arabic":
        return TRANSLATIONS["Arabic"].get(text, text)
    return text


# =========================================================
# LANGUAGE SWITCH FUNCTION
# =========================================================
def switch_language():
    if st.session_state.lang == "English":
        st.session_state.lang = "Arabic"
    else:
        st.session_state.lang = "English"


# =========================================================
# GLOBAL CSS
# =========================================================
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] .stButton {
        width: 100%;
    }

    [data-testid="stSidebar"] .stButton button {
        border: none !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        background-color: transparent !important;
        width: 100%;
        padding: 0.55rem 0.75rem;
        font-size: 1rem;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(128,128,128,0.15) !important;
    }

    .language-switch-container {
        display: flex;
        justify-content: flex-end;
    }

    .arabic-page {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# LANGUAGE SWITCHER
# =========================================================
left_space, middle_space, language_col = st.columns([6, 2, 1])

with language_col:
    if st.session_state.lang == "English":
        st.button(
            "🇱🇧 العربية",
            key="language_button_ar",
            use_container_width=True,
            on_click=switch_language
        )
    else:
        st.button(
            "🇬🇧 English",
            key="language_button_en",
            use_container_width=True,
            on_click=switch_language
        )

# =========================================================
# RTL / LTR
# =========================================================
if st.session_state.lang == "Arabic":
    st.markdown(
        """
        <style>
        .main .block-container {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stSidebar"] {
            direction: rtl;
        }
        [data-testid="stSidebar"] .stButton button {
            text-align: right !important;
        }
        [data-testid="stSidebar"] .stMarkdown {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stSidebar"] label {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .main .block-container {
            direction: ltr;
            text-align: left;
        }
        [data-testid="stSidebar"] {
            direction: ltr;
        }
        [data-testid="stSidebar"] .stButton button {
            text-align: left !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown(f"### {t('Navigation')}")

    pages = [
        "🏠 Home",
        "📊 Overview",
        "📝 Objective Analysis",
        "📈 Class Total Average Analysis",
        "🗺️ MAP Analysis",
        "🎯 Achievement & Gaps",
        "📑 Reports"
    ]

    for p in pages:
        if st.session_state.page == p:
            btn_label = f"▶ {t(p)}"
        else:
            btn_label = t(p)

        if st.button(btn_label, key=f"navigation_{p}", use_container_width=True):
            st.session_state.page = p
            st.rerun()

page = st.session_state.page

# =========================================================
# COLORS
# =========================================================
COLORS = {
    "Absent": "#808080",
    "Fail": "#d62728",
    "Acceptable": "#ff7f0e",
    "Good": "#2ca02c",
    "Very Good": "#1f77b4",
    "Outstanding": "#9467bd"
}

ORDER = ["Absent", "Fail", "Acceptable", "Good", "Very Good", "Outstanding"]

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def color_cell(value):
    if value == t("Growth"):
        return "background-color: green; color: white"
    if value == t("Decay"):
        return "background-color: red; color: white"
    if value == t("Same"):
        return "background-color: yellow; color: black"
    return ""


def support_level(pct):
    if pct is None:
        return t("N/A")

    try:
        p = float(pct)
    except (ValueError, TypeError):
        return t("N/A")

    if pd.isna(p):
        return t("N/A")

    if p < 25:
        return t("Intervention")
    if p < 50:
        return t("Monitor")
    if p < 75:
        return t("On Track")

    return t("Enrichment")


# =========================================================
# ATTENDANCE SUMMARY
# =========================================================
def attendance_summary(df, absent_column="Absent"):
    total_students = len(df)

    if total_students == 0:
        return 0, 0, 0, 0.0

    if absent_column in df.columns:
        absent_students = int(df[absent_column].sum())
    else:
        absent_students = 0

    present_students = total_students - absent_students
    absent_percentage = (absent_students / total_students) * 100

    return (
        total_students,
        present_students,
        absent_students,
        round(absent_percentage, 1)
    )


def show_attendance_metrics(
    total_students,
    present_students,
    absent_students,
    absent_percentage
):
    st.markdown("---")

    st.subheader("📊 " + t("Attendance / Assessment Participation"))

    a1, a2, a3, a4 = st.columns(4)

    a1.metric(
        t("Total Students"),
        total_students
    )

    a2.metric(
        t("Present / Assessed"),
        present_students
    )

    a3.metric(
        t("Absent Students"),
        absent_students
    )

    a4.metric(
        t("Absent %"),
        f"{absent_percentage:.1f}%"
    )

    st.caption(
        f"{absent_percentage:.1f}% {t('of total students')} "
        f"({absent_students} / {total_students})"
    )


# =========================================================
# EXCEL TEMPLATE HELPERS
# =========================================================
def save_workbook_to_bytes(data, sheet_name="Assessment"):
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    for row in data:
        ws.append(row)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()


def objectives_template():
    data = [
        ["Teacher Name: Example Teacher", "Class: Grade 7A", "Date: 27/08/2026",
         "Assessment name: Quiz 1", "Subject: Mathematics"],
        ["Student Name", "Objective 1", "Objective 2", "Objective 3", ""],
        ["", "Fractions", "Algebra", "Geometry", ""],
        ["Points for Objectives", 10, 15, 5, ""],
        ["Student 1", 8, 12, 4, ""],
        ["Student 2", 10, 14, 5, ""],
        ["Student 3", "A", "A", "A", ""]
    ]

    return save_workbook_to_bytes(data)


def total_template():
    data = [
        ["Teacher Name: Example Teacher", "Class: Grade 7A", "Date: 27/08/2026",
         "Assessment name: Internal Assessment", "Subject: Mathematics"],
        ["Student Name", "Total"],
        ["Total", 100],
        ["Student 1", 82],
        ["Student 2", 91],
        ["Student 3", 65]
    ]

    return save_workbook_to_bytes(data)


def gaps_template():
    data = [
        ["Teacher Name: Example Teacher", "Class: Grade 7A", "Date: 27/08/2026",
         "Assessment name: Internal vs MAP", "Subject: Mathematics"],
        ["Student Name", "Total of Internal", "Percentile of MAP"],
        ["Over", 100, ""],
        ["Student 1", 82, 75],
        ["Student 2", 91, 88],
        ["Student 3", 65, 50]
    ]

    return save_workbook_to_bytes(data)


def map_template():
    data = {
        "Student Name": ["Student 1", "Student 2", "Student 3", "Student 4"],
        "Grade": [7, 7, 7, 7],
        "Subject": ["Mathematics", "Mathematics", "Mathematics", "Mathematics"],
        "Previous RIT": [205, 210, 198, 215],
        "Current RIT": [210, 214, 200, 218],
        "Percentile": [55, 70, 40, 85]
    }

    df = pd.DataFrame(data)
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="MAP Data")

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# READ OBJECTIVES FILE
# =========================================================
def read_objectives_file(file):
    try:
        file.seek(0)

        meta_raw = pd.read_excel(file, nrows=1, header=None)

        meta = {}

        for value in meta_raw.iloc[0].tolist():
            text = str(value).strip()

            if ":" in text:
                key, value_part = text.split(":", 1)
                meta[key.strip()] = value_part.strip()

        file.seek(0)

        df = pd.read_excel(file, header=1)

        if df.empty:
            return None, None

        first_col = df.columns[0]

        mask = (
            df[first_col]
            .astype(str)
            .str.strip()
            .str.lower()
            == "points for objectives"
        )

        if not mask.any():
            return None, None

        max_row = df[mask].iloc[0]

        valid_cols = []
        total_max = 0.0

        for column in df.columns:

            if column == first_col:
                continue

            header = str(column).strip()

            if (
                header == ""
                or header.lower() == "nan"
                or header.startswith("Unnamed")
            ):
                continue

            try:
                max_value = float(max_row[column])
            except (ValueError, TypeError):
                continue

            if max_value > 0:
                valid_cols.append(column)
                total_max += max_value

        if not valid_cols:
            return None, None

        # Remove Points for Objectives row
        df = df[~mask].copy()

        df = df.rename(
            columns={first_col: "Student Name"}
        )

        df = df.dropna(
            subset=["Student Name"]
        )

        keep_columns = ["Student Name"] + valid_cols

        df = df[keep_columns].copy()

        # -----------------------------------------------------
        # IMPORTANT:
        # DO NOT convert absent students to ZERO.
        # Preserve them as NaN and identify them separately.
        # -----------------------------------------------------
        def detect_absent(row):
            all_empty = True
            has_absent_marker = False

            for column in valid_cols:

                value = row[column]

                if isinstance(value, str):

                    text = value.strip().lower()

                    if text in ["a", "absent"]:
                        has_absent_marker = True

                    elif text != "":
                        all_empty = False

                elif not pd.isna(value):
                    all_empty = False

            return has_absent_marker or all_empty

        df["Absent"] = df.apply(
            detect_absent,
            axis=1
        )

        # Convert valid marks to numbers.
        # Invalid/blank values remain NaN.
        for column in valid_cols:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # -----------------------------------------------------
        # Total and percentage
        # Only present students receive a percentage.
        # -----------------------------------------------------
        df["Obtained"] = df[valid_cols].sum(
            axis=1,
            min_count=1
        )

        df.loc[
            df["Absent"],
            "Obtained"
        ] = pd.NA

        df["Pct"] = (
            df["Obtained"] / total_max * 100
        ).round(1)

        df.loc[
            df["Absent"],
            "Pct"
        ] = pd.NA

        return meta, df

    except Exception:
        return None, None


# =========================================================
# READ TOTAL FILE
# =========================================================
def read_total_file(file):
    try:
        file.seek(0)

        raw = pd.read_excel(
            file,
            header=None
        )

        if raw.empty:
            return None, None

        meta = {}

        for value in raw.iloc[0].tolist():

            text = str(value).strip()

            if ":" in text:
                key, value_part = text.split(":", 1)
                meta[key.strip()] = value_part.strip()

        headers = [
            str(value).strip()
            for value in raw.iloc[1].tolist()
        ]

        total_idx = None

        for i in range(2, len(raw)):

            if "total" in str(
                raw.iloc[i, 0]
            ).lower():

                total_idx = i
                break

        if total_idx is None:
            return None, None

        try:
            max_total = float(
                raw.iloc[total_idx, 1]
            )
        except (ValueError, TypeError):
            max_total = 100.0

        data = raw.iloc[2:].copy()

        data.columns = headers

        data = data[
            ~data.iloc[:, 0]
            .astype(str)
            .str.lower()
            .str.contains(
                "total",
                na=False
            )
        ]

        data = data.rename(
            columns={
                data.columns[0]:
                "Student Name"
            }
        )

        total_columns = [
            c for c in data.columns
            if "total" in str(c).lower()
        ]

        if not total_columns:
            return None, None

        total_column = total_columns[0]

        # -----------------------------------------------------
        # Preserve blank/absent values.
        # -----------------------------------------------------
        original_values = data[total_column].copy()

        data[total_column] = pd.to_numeric(
            data[total_column],
            errors="coerce"
        )

        data["Absent"] = original_values.apply(
            lambda x:
                isinstance(x, str)
                and x.strip().lower()
                in ["a", "absent"]
        )

        # Completely blank score = absent
        data.loc[
            data[total_column].isna(),
            "Absent"
        ] = True

        data["Pct"] = (
            data[total_column]
            / max_total
            * 100
        ).round(1)

        data.loc[
            data["Absent"],
            "Pct"
        ] = pd.NA

        return meta, data

    except Exception:
        return None, None


# =========================================================
# READ GAPS FILE
# =========================================================
def read_gaps_file(file):
    try:
        file.seek(0)

        raw = pd.read_excel(
            file,
            header=None
        )

        if raw.empty:
            return None, None

        meta = {}

        for value in raw.iloc[0].tolist():

            text = str(value).strip()

            if ":" in text:
                key, value_part = text.split(":", 1)
                meta[key.strip()] = value_part.strip()

        headers = [
            str(value).strip()
            for value in raw.iloc[1].tolist()
        ]

        over_idx = None

        for i in range(2, len(raw)):

            if "over" in str(
                raw.iloc[i, 0]
            ).lower():

                over_idx = i
                break

        if over_idx is None:
            return None, None

        try:
            max_total = float(
                raw.iloc[over_idx, 1]
            )
        except (ValueError, TypeError):
            max_total = 100.0

        data = raw.iloc[2:].copy()

        data.columns = headers

        data = data[
            ~data.iloc[:, 0]
            .astype(str)
            .str.lower()
            .str.contains(
                "over",
                na=False
            )
        ]

        data = data.rename(
            columns={
                data.columns[0]:
                "Student Name"
            }
        )

        internal_columns = [
            c for c in data.columns
            if "total of internal"
            in str(c).lower()
        ]

        map_columns = [
            c for c in data.columns
            if "percentile of map"
            in str(c).lower()
        ]

        if not internal_columns or not map_columns:
            return None, None

        internal_column = internal_columns[0]
        map_column = map_columns[0]

        data[internal_column] = pd.to_numeric(
            data[internal_column],
            errors="coerce"
        )

        data[map_column] = pd.to_numeric(
            data[map_column],
            errors="coerce"
        )

        data["Pct1"] = (
            data[internal_column]
            / max_total
            * 100
        ).round(1)

        data["Pct2"] = data[
            map_column
        ].round(1)

        # -----------------------------------------------------
        # Student is considered absent/not assessed if either
        # required assessment result is missing.
        # -----------------------------------------------------
        data["Absent"] = (
            data["Pct1"].isna()
            | data["Pct2"].isna()
        )

        data.loc[
            data["Absent"],
            ["Pct1", "Pct2"]
        ] = pd.NA

        data = data[
            [
                "Student Name",
                "Pct1",
                "Pct2",
                "Absent"
            ]
        ]

        return meta, data

    except Exception:
        return None, None


# =========================================================
# READ SECTION FILE
# =========================================================
def read_section_file(file):
    meta, df = read_objectives_file(file)

    if meta is None or df is None:
        return None, None, None, None, None

    try:
        file.seek(0)

        raw_full = pd.read_excel(
            file,
            header=1
        )

        first_value = str(
            raw_full.iloc[0, 0]
        ).strip().lower()

        if first_value != "points for objectives":
            desc_row = raw_full.iloc[0]
        else:
            desc_row = None

        obj_names = [
            c for c in df.columns
            if c not in [
                "Student Name",
                "Obtained",
                "Pct",
                "Absent"
            ]
        ]

        points_mask = (
            raw_full.iloc[:, 0]
            .astype(str)
            .str.strip()
            .str.lower()
            == "points for objectives"
        )

        if points_mask.any():
            max_row = raw_full[
                points_mask
            ].iloc[0]
        else:
            return None, None, None, None, None

        obj_max = {}
        obj_desc = {}

        for column in obj_names:

            try:
                obj_max[column] = float(
                    max_row[column]
                )
            except (ValueError, TypeError):
                obj_max[column] = 0

            if desc_row is not None:

                description = str(
                    desc_row[column]
                ).strip()

                if (
                    description == ""
                    or description.lower() == "nan"
                ):
                    description = str(column)

            else:
                description = str(column)

            obj_desc[column] = description

        return (
            meta,
            df,
            obj_names,
            obj_max,
            obj_desc
        )

    except Exception:
        return None, None, None, None, None


# =========================================================
# HOME
# =========================================================
if page == "🏠 Home":

    if os.path.exists("logo.png"):
        st.image(
            "logo.png",
            width=120
        )

    st.title(
        t("Assessment Analysis")
    )

    st.markdown(
        f"### {t('Student Assessment & Achievement Dashboard')}"
    )

    st.markdown(
        t(
            "Analyze MAP, internal assessments, grades, and student performance in seconds."
        )
    )

    st.markdown("---")

    st.markdown(
        f"### {t('📌 How to use')}"
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"### {t('① Upload Data')}"
        )
        st.write(
            t(
                "Upload your Excel files with student marks."
            )
        )

    with c2:
        st.markdown(
            f"### {t('② Choose Analysis')}"
        )
        st.write(
            t(
                "Pick the analysis type from the sidebar."
            )
        )

    with c3:
        st.markdown(
            f"### {t('③ View Insights')}"
        )
        st.write(
            t(
                "See charts, gaps, and download reports."
            )
        )

    st.info(
        t(
            "Use the sidebar on the left to navigate to your analysis."
        )
    )


# =========================================================
# OVERVIEW
# =========================================================
elif page == "📊 Overview":

    st.title(
        t("📊 Assessment Analysis Overview")
    )

    st.markdown(
        t(
            "The Assessment Analysis tool is designed to help teachers, coordinators, "
            "and school leaders analyze student achievement quickly and consistently."
        )
    )

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader(
            t("📝 Objective Analysis")
        )

        st.write(
            t(
                "Analyze one assessment at a time using learning objectives and student marks."
            )
        )

    with c2:
        st.subheader(
            t("📈 Class Total Average Analysis")
        )

        st.write(
            t(
                "Compare multiple assessments for the same class and monitor the class average progress over time."
            )
        )

    with c3:
        st.subheader(
            t("🎯 Achievement & Gaps")
        )

        st.write(
            t(
                "Compare Internal Assessment results with MAP Percentile in one sheet to identify achievement gaps."
            )
        )

    st.markdown("---")

    st.subheader(
        t("🗺️ MAP Analysis")
    )

    st.write(
        t(
            "The MAP Analysis section allows you to compare previous and current RIT scores, growth, and percentile performance."
        )
    )


# =========================================================
# OBJECTIVE ANALYSIS
# =========================================================
elif page == "📝 Objective Analysis":

    st.header(
        t("📝 Objective Analysis")
    )

    st.markdown(
        t(
            "Analyze a single assessment based on learning objectives and student marks."
        )
    )

    st.download_button(
        t("📥 Download Excel Template"),
        objectives_template(),
        "Student_Analysis_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    st.header(
        t("Step 1: Upload Student Marks Excel")
    )

    st.info(
        t(
            "Row 1: Assessment Information\n"
            "Row 2: Headers (Objective names)\n"
            "Row 3: Objective Descriptions\n"
            "Row 4: 'Points for Objectives' + Maximum Marks\n"
            "Row 5+: Student Marks\n"
            "Leave empty or enter 'A' for absent students."
        )
    )

    up_file = st.file_uploader(
        t("Upload Excel"),
        type=["xlsx", "xls"],
        key="single_objective_file"
    )

    if up_file:

        meta, parsed_df = read_objectives_file(
            up_file
        )

        if meta is None or parsed_df is None:
            st.error(
                t(
                    "❌ Need 'Points for Objectives' row."
                )
            )
            st.stop()

        st.subheader(
            t("📋 Info")
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.markdown(
            f"**{t('👩‍🏫 Teacher:')}** "
            f"{meta.get('Teacher Name', 'N/A')}"
        )

        m2.markdown(
            f"**{t('🏫 Class:')}** "
            f"{meta.get('Class', 'N/A')}"
        )

        m3.markdown(
            f"**{t('📅 Date:')}** "
            f"{meta.get('Date', 'N/A')}"
        )

        m4.markdown(
            f"**{t('📝 Assessment:')}** "
            f"{meta.get('Assessment name', 'N/A')}"
        )

        st.markdown(
            f"### 📝 {t('Name:')} "
            f"**{meta.get('Assessment name', 'N/A')}** "
            f"| 📚 {t('Subject:')} "
            f"**{meta.get('Subject', 'N/A')}**"
        )

        up_file.seek(0)

        raw = pd.read_excel(
            up_file,
            header=1
        )

        first_value = str(
            raw.iloc[0, 0]
        ).strip().lower()

        if first_value != "points for objectives":

            desc_row = raw.iloc[0]

            raw_students = (
                raw.iloc[1:]
                .reset_index(drop=True)
            )

        else:

            desc_row = None
            raw_students = raw.copy()

        first_column = raw_students.columns[0]

        obj_desc = {}

        for column in raw_students.columns:

            if column == first_column:
                continue

            if desc_row is not None:

                description = str(
                    desc_row[column]
                ).strip()

                if (
                    description == ""
                    or description.lower() == "nan"
                ):
                    description = str(column)

            else:
                description = str(column)

            obj_desc[column] = description

        mask = (
            raw_students[first_column]
            .astype(str)
            .str.strip()
            .str.lower()
            == "points for objectives"
        )

        if not mask.any():

            st.error(
                t(
                    "❌ Need 'Points for Objectives' row."
                )
            )

            st.stop()

        max_row = raw_students[
            mask
        ].iloc[0]

        obj_names = []
        obj_max = []

        for column in raw_students.columns:

            if column == first_column:
                continue

            header = str(column).strip()

            if (
                header == ""
                or header.lower() == "nan"
                or header.startswith("Unnamed")
            ):
                continue

            try:
                maximum = float(
                    max_row[column]
                )
            except (ValueError, TypeError):
                continue

            if maximum > 0:
                obj_names.append(column)
                obj_max.append(maximum)

        student_df = raw_students[
            ~mask
        ].copy()

        student_df = student_df.dropna(
            subset=[first_column]
        )

        student_df = student_df.rename(
            columns={
                first_column:
                "Student Name"
            }
        )

        student_df = student_df[
            ["Student Name"] + obj_names
        ].copy()

        # -----------------------------------------------------
        # ABSENCE DETECTION
        # -----------------------------------------------------
        def is_absent(row):

            has_a = False
            all_empty = True

            for column in obj_names:

                value = row[column]

                if isinstance(value, str):

                    text = value.strip().lower()

                    if text in [
                        "a",
                        "absent"
                    ]:
                        has_a = True

                    elif text != "":
                        all_empty = False

                elif not pd.isna(value):
                    all_empty = False

            return has_a or all_empty

        student_df["Absent"] = student_df.apply(
            is_absent,
            axis=1
        )

        # -----------------------------------------------------
        # IMPORTANT:
        # Convert marks to numbers but KEEP absent students
        # as NaN, not ZERO.
        # -----------------------------------------------------
        for column in obj_names:

            student_df[column] = pd.to_numeric(
                student_df[column],
                errors="coerce"
            )

        total_max = sum(obj_max)

        # Total only for present students
        student_df["Obtained"] = student_df[
            obj_names
        ].sum(
            axis=1,
            min_count=1
        )

        student_df.loc[
            student_df["Absent"],
            "Obtained"
        ] = pd.NA

        student_df["Pct"] = (
            student_df["Obtained"]
            / total_max
            * 100
        ).round(1)

        student_df.loc[
            student_df["Absent"],
            "Pct"
        ] = pd.NA

        # -----------------------------------------------------
        # ATTENDANCE SUMMARY
        # -----------------------------------------------------
        total_students, present_students, absent_students, absent_percentage = attendance_summary(
            student_df
        )

        show_attendance_metrics(
            total_students,
            present_students,
            absent_students,
            absent_percentage
        )

        st.info(
            f"ℹ️ {t('Absent students are excluded from all achievement and percentage calculations.')}"
        )

        st.info(
            f"📋 {t('Auto Total Max Mark')} = "
            f"**{total_max:g}**"
        )

        st.markdown(
            f"### 📚 {t('Objectives')}"
        )

        for index, obj in enumerate(
            obj_names,
            1
        ):

            st.markdown(
                f"{index}. **{obj}** – "
                f"{obj_desc.get(obj, obj)}"
            )

        errors = []

        for _, row in student_df.iterrows():

            if row["Absent"]:
                continue

            for index, column in enumerate(
                obj_names
            ):

                value = float(
                    row[column]
                )

                if value > obj_max[index]:

                    errors.append(
                        f"• {row['Student Name']}: "
                        f"{column}={value} > "
                        f"max {obj_max[index]}"
                    )

                if value < 0:

                    errors.append(
                        f"• {row['Student Name']}: "
                        f"{column} Negative"
                    )

        st.subheader(
            t("📊 Preview")
        )

        st.dataframe(
            student_df,
            use_container_width=True
        )

        if errors:

            st.error(
                t("🚫 Fix data entry:")
                + "\n"
                + "\n".join(errors)
            )

        else:

            if st.button(
                t("Analyze Assessment"),
                key="analyze_assessment_button"
            ):

                results = []

                for _, row in student_df.iterrows():

                    if row["Absent"]:

                        results.append({
                            "Student Name":
                                row["Student Name"],
                            "Total": "-",
                            "Total %": None,
                            "Level":
                                t("Absent")
                        })

                        continue

                    # =====================================================
                    # EXCEL-ALIGNED TOTAL CALCULATION
                    # =====================================================
                    total_obtained = sum(
                        float(row[column])
                        for column in obj_names
                    )

                    total_percentage = (
                        (
                            total_obtained
                            / total_max
                        )
                        * 100
                        if total_max > 0
                        else 0
                    )

                    if total_percentage < 60:
                        level = t("Fail")

                    elif total_percentage < 70:
                        level = t("Acceptable")

                    elif total_percentage < 80:
                        level = t("Good")

                    elif total_percentage < 90:
                        level = t("Very Good")

                    else:
                        level = t("Outstanding")

                    results.append({
                        "Student Name":
                            row["Student Name"],
                        "Total":
                            total_obtained,
                        "Total %":
                            round(
                                total_percentage,
                                1
                            ),
                        "Level":
                            level
                    })

                rdf = pd.DataFrame(
                    results
                )

                rdf["Support Level"] = rdf[
                    "Total %"
                ].apply(
                    support_level
                )

                st.header(
                    t("Step 2: Analysis Report")
                )

                # -----------------------------------------------------
                # Attendance displayed beside analysis
                # -----------------------------------------------------
                show_attendance_metrics(
                    total_students,
                    present_students,
                    absent_students,
                    absent_percentage
                )

                counts = rdf[
                    "Level"
                ].value_counts().to_dict()

                c1, c2, c3, c4, c5, c6 = st.columns(6)

                c1.metric(
                    t("Absent"),
                    counts.get(
                        t("Absent"),
                        0
                    )
                )

                c2.metric(
                    t("Fail"),
                    counts.get(
                        t("Fail"),
                        0
                    )
                )

                c3.metric(
                    t("Acceptable"),
                    counts.get(
                        t("Acceptable"),
                        0
                    )
                )

                c4.metric(
                    t("Good"),
                    counts.get(
                        t("Good"),
                        0
                    )
                )

                c5.metric(
                    t("Very Good"),
                    counts.get(
                        t("Very Good"),
                        0
                    )
                )

                c6.metric(
                    t("Outstanding"),
                    counts.get(
                        t("Outstanding"),
                        0
                    )
                )

                # -----------------------------------------------------
                # ONLY PRESENT STUDENTS USED HERE
                # -----------------------------------------------------
                valid_percentages = rdf[
                    "Total %"
                ].dropna()

                total_students_for_analysis = len(
                    valid_percentages
                )

                if total_students_for_analysis > 0:

                    percentage_60_or_more = (
                        (
                            valid_percentages >= 60
                        ).sum()
                        / total_students_for_analysis
                        * 100
                    )

                    percentage_above_60 = (
                        (
                            valid_percentages > 60
                        ).sum()
                        / total_students_for_analysis
                        * 100
                    )

                    percentage_above_75 = (
                        (
                            valid_percentages > 75
                        ).sum()
                        / total_students_for_analysis
                        * 100
                    )

                else:

                    percentage_60_or_more = 0
                    percentage_above_60 = 0
                    percentage_above_75 = 0

                if percentage_above_75 >= 90:

                    overall = t("Outstanding")

                elif percentage_above_60 >= 90:

                    overall = t("Very Good")

                elif percentage_above_60 >= 75:

                    overall = t("Good")

                elif percentage_60_or_more >= 60:

                    overall = t("Acceptable")

                else:

                    overall = t("Below Acceptable")

                st.success(
                    f"**{overall}** "
                    f"({t('Max')} {total_max:g})"
                )

                level_df = (
                    rdf["Level"]
                    .value_counts()
                    .reset_index()
                )

                level_df.columns = [
                    "Level",
                    "Count"
                ]

                ordered_levels = [
                    t(level)
                    for level in ORDER
                ]

                level_df["Level"] = pd.Categorical(
                    level_df["Level"],
                    categories=ordered_levels,
                    ordered=True
                )

                level_df = level_df.sort_values(
                    "Level"
                )

                v1, v2 = st.columns(2)

                with v1:

                    st.subheader(
                        t("📊 Student Achievement")
                    )

                    chart_df = rdf.dropna(
                        subset=["Total %"]
                    )

                    fig = px.bar(
                        chart_df,
                        x="Student Name",
                        y="Total %",
                        color="Level",
                        range_y=[0, 100]
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                with v2:

                    st.subheader(
                        t("📊 Level Distribution")
                    )

                    pie_fig = px.pie(
                        level_df,
                        names="Level",
                        values="Count",
                        color="Level",
                        color_discrete_map={
                            t(key): value
                            for key, value
                            in COLORS.items()
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

                st.subheader(
                    t("🎯 Student Support Levels")
                )

                support_chart_df = rdf.dropna(
                    subset=["Total %"]
                )

                support_fig = px.bar(
                    support_chart_df,
                    x="Student Name",
                    y="Total %",
                    color="Support Level",
                    range_y=[0, 100]
                )

                st.plotly_chart(
                    support_fig,
                    use_container_width=True
                )

                # -----------------------------------------------------
                # SUPPORT GROUPS
                # Exclude N/A / absent students
                # -----------------------------------------------------
                support_count = (
                    rdf[
                        rdf["Total %"].notna()
                    ]["Support Level"]
                    .value_counts()
                    .reset_index()
                )

                support_count.columns = [
                    t("Support Level"),
                    t("Students")
                ]

                st.subheader(
                    t("👥 Support Groups")
                )

                st.dataframe(
                    support_count,
                    use_container_width=True
                )

                st.dataframe(
                    rdf,
                    use_container_width=True
                )

                excel_buffer = io.BytesIO()

                rdf.to_excel(
                    excel_buffer,
                    index=False
                )

                st.download_button(
                    t("📊 Download Excel"),
                    excel_buffer.getvalue(),
                    "Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


# =========================================================
# CLASS TOTAL AVERAGE ANALYSIS
# =========================================================
elif page == "📈 Class Total Average Analysis":

    st.header(
        t("📈 Class Total Average Analysis")
    )

    st.download_button(
        t("📥 Download Excel Template"),
        objectives_template(),
        "Grade_Analysis_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.info(
        t(
            "Choose the number of assessments. Upload files using the same Excel format as Objective Analysis."
        )
    )

    n_assessments = st.number_input(
        t("🔢 Number of assessments"),
        min_value=2,
        max_value=10,
        value=2,
        step=1,
        key="number_of_assessments"
    )

    assessment_files = []

    for index in range(
        int(n_assessments)
    ):

        assessment_files.append(
            st.file_uploader(
                f"📄 {t('Assessment')} {index + 1}",
                type=["xlsx", "xls"],
                key=f"assessment_upload_{index}"
            )
        )

    if all(assessment_files):

        metadata_list = []
        merged = None
        percentage_columns = []
        absent_columns = []

        for index, file in enumerate(
            assessment_files
        ):

            meta, df = read_objectives_file(
                file
            )

            if meta is None or df is None:

                st.error(
                    t(
                        "❌ File missing 'Points for Objectives' row."
                    )
                )

                st.stop()

            metadata_list.append(meta)

            percentage_column = (
                f"Pct{index + 1}"
            )

            absent_column = (
                f"Absent{index + 1}"
            )

            keep = df[
                [
                    "Student Name",
                    "Pct",
                    "Absent"
                ]
            ].rename(
                columns={
                    "Pct":
                        percentage_column,
                    "Absent":
                        absent_column
                }
            )

            if merged is None:

                merged = keep

            else:

                merged = pd.merge(
                    merged,
                    keep,
                    on="Student Name",
                    how="outer"
                )

            percentage_columns.append(
                percentage_column
            )

            absent_columns.append(
                absent_column
            )

        st.subheader(
            t("📋 Assessment Information")
        )

        for index, metadata in enumerate(
            metadata_list
        ):

            st.markdown(
                f"**File {index + 1}: "
                f"{metadata.get('Assessment name', 'N/A')}** | "
                f"👩‍🏫 {metadata.get('Teacher Name', 'N/A')} | "
                f"🏫 {metadata.get('Class', 'N/A')} | "
                f"📅 {metadata.get('Date', 'N/A')} | "
                f"📚 {metadata.get('Subject', 'N/A')}"
            )

        # -----------------------------------------------------
        # DO NOT FILL ABSENT WITH ZERO.
        # Keep missing scores as NaN.
        # -----------------------------------------------------

        # Overall attendance based on unique students
        total_class_students = len(
            merged
        )

        last_absent_col = absent_columns[-1]

        merged[last_absent_col] = (
            merged[last_absent_col]
            .fillna(True)
            .astype(bool)
        )

        present_last = (
            ~merged[last_absent_col]
        )

        absent_last_count = int(
            merged[last_absent_col].sum()
        )

        present_last_count = int(
            present_last.sum()
        )

        absent_last_percentage = (
            absent_last_count
            / total_class_students
            * 100
            if total_class_students > 0
            else 0
        )

        show_attendance_metrics(
            total_class_students,
            present_last_count,
            absent_last_count,
            round(
                absent_last_percentage,
                1
            )
        )

        # -----------------------------------------------------
        # GROWTH:
        # Only students who have valid results in BOTH
        # assessments are included.
        # -----------------------------------------------------
        first_col = percentage_columns[0]
        last_col = percentage_columns[-1]

        merged["Difference"] = (
            merged[last_col]
            - merged[first_col]
        ).round(1)

        merged["Status"] = merged[
            "Difference"
        ].apply(
            lambda difference:
                t("N/A")
                if pd.isna(difference)
                else
                t("Growth")
                if difference > 0.5
                else
                t("Decay")
                if difference < -0.5
                else
                t("Same")
        )

        merged["Support Level"] = merged[
            last_col
        ].apply(
            support_level
        )

        st.subheader(
            t("📊 Comparison Table (Percentage Based)")
        )

        st.dataframe(
            merged.style.map(
                color_cell,
                subset=["Status"]
            ),
            use_container_width=True
        )

        status_counts = (
            merged[
                merged["Difference"].notna()
            ]["Status"]
            .value_counts()
            .to_dict()
        )

        growth_count = status_counts.get(
            t("Growth"),
            0
        )

        decay_count = status_counts.get(
            t("Decay"),
            0
        )

        same_count = status_counts.get(
            t("Same"),
            0
        )

        st.subheader(
            t("📢 Summary")
        )

        m1, m2, m3 = st.columns(3)

        m1.metric(
            f"🟩 {t('Growth')}",
            growth_count
        )

        m2.metric(
            f"🟥 {t('Decay')}",
            decay_count
        )

        m3.metric(
            f"🟨 {t('Same')}",
            same_count
        )

        status_df = pd.DataFrame({
            "Status": [
                t("Growth"),
                t("Decay"),
                t("Same")
            ],
            "Count": [
                growth_count,
                decay_count,
                same_count
            ]
        })

        v1, v2 = st.columns(2)

        with v1:

            st.markdown(
                f"**{t('Bar Chart')}**"
            )

            bar_fig = px.bar(
                status_df,
                x="Status",
                y="Count",
                color="Status",
                color_discrete_map={
                    t("Growth"): "green",
                    t("Decay"): "red",
                    t("Same"): "yellow"
                }
            )

            st.plotly_chart(
                bar_fig,
                use_container_width=True
            )

        with v2:

            st.markdown(
                f"**{t('Pie Chart')}**"
            )

            pie_fig = px.pie(
                status_df,
                names="Status",
                values="Count",
                color="Status",
                color_discrete_map={
                    t("Growth"): "green",
                    t("Decay"): "red",
                    t("Same"): "yellow"
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

        # -----------------------------------------------------
        # CLASS AVERAGE:
        # NaN values are automatically excluded.
        # Therefore absent students do NOT lower the average.
        # -----------------------------------------------------
        average_data = (
            merged[
                percentage_columns
            ]
            .mean(
                skipna=True
            )
            .reset_index()
        )

        average_data.columns = [
            "Assessment",
            "Average"
        ]

        average_data["Assessment"] = (
            average_data["Assessment"]
            .str.replace(
                "Pct",
                "Assess",
                regex=False
            )
        )

        st.subheader(
            t("📈 Average Score Trend (%)")
        )

        average_fig = px.line(
            average_data,
            x="Assessment",
            y="Average",
            markers=True
        )

        st.plotly_chart(
            average_fig,
            use_container_width=True
        )

        st.subheader(
            t("📈 Student Growth (Difference)")
        )

        growth_fig = px.bar(
            merged[
                merged["Difference"].notna()
            ],
            x="Student Name",
            y="Difference",
            color="Status"
        )

        st.plotly_chart(
            growth_fig,
            use_container_width=True
        )

        support_count = (
            merged[
                merged[last_col].notna()
            ]["Support Level"]
            .value_counts()
            .reset_index()
        )

        support_count.columns = [
            t("Support Level"),
            t("Students")
        ]

        st.subheader(
            t("👥 Support Groups")
        )

        st.dataframe(
            support_count,
            use_container_width=True
        )

        comparison_buffer = io.BytesIO()

        merged.to_excel(
            comparison_buffer,
            index=False
        )

        st.download_button(
            t("📊 Download Comparison Excel"),
            comparison_buffer.getvalue(),
            "Comparison.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# MAP ANALYSIS
# =========================================================
elif page == "🗺️ MAP Analysis":

    st.title(
        t("🗺️ MAP Analysis")
    )

    st.info(
        f"### {t('What is a RIT Score?')}\n"
        f"{t('The RIT score is the scale used by MAP Growth to measure student achievement.')}"
    )

    st.download_button(
        t("📥 Download MAP Excel Template"),
        map_template(),
        "MAP_Analysis_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    map_file = st.file_uploader(
        t("📄 Upload MAP Data Excel"),
        type=["xlsx", "xls"],
        key="map_upload"
    )

    if map_file:

        try:

            map_df = pd.read_excel(
                map_file
            )

            required_columns = [
                "Student Name",
                "Grade",
                "Subject",
                "Previous RIT",
                "Current RIT",
                "Percentile"
            ]

            missing_columns = [
                c for c in required_columns
                if c not in map_df.columns
            ]

            if missing_columns:

                st.error(
                    t("❌ Missing columns: ")
                    + ", ".join(
                        missing_columns
                    )
                )

                st.stop()

            for column in [
                "Previous RIT",
                "Current RIT",
                "Percentile"
            ]:

                map_df[column] = pd.to_numeric(
                    map_df[column],
                    errors="coerce"
                )

            # -----------------------------------------------------
            # A MAP student is considered absent/not assessed
            # when the required MAP values are missing.
            # -----------------------------------------------------
            map_df["Absent"] = (
                map_df[
                    [
                        "Previous RIT",
                        "Current RIT",
                        "Percentile"
                    ]
                ]
                .isna()
                .any(axis=1)
            )

            map_df["RIT Growth"] = (
                map_df["Current RIT"]
                - map_df["Previous RIT"]
            )

            map_df.loc[
                map_df["Absent"],
                "RIT Growth"
            ] = pd.NA

            map_df["Growth Status"] = map_df[
                "RIT Growth"
            ].apply(
                lambda value:
                    t("N/A")
                    if pd.isna(value)
                    else
                    t("Growth")
                    if value > 0
                    else
                    t("Decay")
                    if value < 0
                    else
                    t("Same")
            )

            map_df["Support Level"] = map_df[
                "Percentile"
            ].apply(
                support_level
            )

            st.subheader(
                t("📋 MAP Data Preview")
            )

            st.dataframe(
                map_df,
                use_container_width=True
            )

            st.markdown("---")

            st.subheader(
                t("📊 MAP Summary")
            )

            total_students = len(
                map_df
            )

            absent_students = int(
                map_df["Absent"].sum()
            )

            present_students = (
                total_students
                - absent_students
            )

            absent_percentage = (
                absent_students
                / total_students
                * 100
                if total_students > 0
                else 0
            )

            average_previous = (
                map_df["Previous RIT"]
                .mean(
                    skipna=True
                )
            )

            average_current = (
                map_df["Current RIT"]
                .mean(
                    skipna=True
                )
            )

            average_growth = (
                map_df["RIT Growth"]
                .mean(
                    skipna=True
                )
            )

            average_percentile = (
                map_df["Percentile"]
                .mean(
                    skipna=True
                )
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                t("👥 Students"),
                total_students
            )

            c2.metric(
                t("📉 Previous Avg RIT"),
                round(
                    average_previous,
                    1
                )
            )

            c3.metric(
                t("📈 Current Avg RIT"),
                round(
                    average_current,
                    1
                )
            )

            c4.metric(
                t("🚀 Average Growth"),
                round(
                    average_growth,
                    1
                )
            )

            st.metric(
                t("🎯 Average Percentile"),
                round(
                    average_percentile,
                    1
                )
            )

            # Attendance shown separately
            show_attendance_metrics(
                total_students,
                present_students,
                absent_students,
                round(
                    absent_percentage,
                    1
                )
            )

            st.markdown("---")

            status_count = (
                map_df[
                    map_df["RIT Growth"].notna()
                ]["Growth Status"]
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
                    t("📈 Student Growth")
                )

                growth_fig = px.bar(
                    map_df[
                        map_df["RIT Growth"].notna()
                    ],
                    x="Student Name",
                    y="RIT Growth",
                    color="Growth Status"
                )

                st.plotly_chart(
                    growth_fig,
                    use_container_width=True
                )

            with v2:

                st.subheader(
                    t("📊 Growth Distribution")
                )

                growth_pie = px.pie(
                    status_count,
                    names="Status",
                    values="Count",
                    hole=0.3
                )

                st.plotly_chart(
                    growth_pie,
                    use_container_width=True
                )

            st.markdown("---")

            st.subheader(
                t("🎯 Student Percentile")
            )

            percentile_fig = px.bar(
                map_df[
                    map_df["Percentile"].notna()
                ],
                x="Student Name",
                y="Percentile",
                color="Support Level",
                range_y=[0, 100]
            )

            st.plotly_chart(
                percentile_fig,
                use_container_width=True
            )

            st.subheader(
                t("👥 Support Groups")
            )

            support_count = (
                map_df[
                    map_df["Percentile"].notna()
                ]["Support Level"]
                .value_counts()
                .reset_index()
            )

            support_count.columns = [
                t("Support Level"),
                t("Students")
            ]

            st.dataframe(
                support_count,
                use_container_width=True
            )

            st.subheader(
                t("📋 Student MAP Analysis")
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
                t("📥 Download MAP Analysis"),
                map_buffer.getvalue(),
                "MAP_Analysis_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as error:

            st.error(
                t("❌ Error reading MAP file: ")
                + str(error)
            )


# =========================================================
# ACHIEVEMENT & GAPS
# =========================================================
elif page == "🎯 Achievement & Gaps":

    st.header(
        t("🎯 Achievement & Gaps (Internal vs MAP)")
    )

    st.download_button(
        t("📥 Download Excel Template"),
        gaps_template(),
        "Achievement_Gaps_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    gaps_file = st.file_uploader(
        t("📄 Upload Single Sheet"),
        type=["xlsx", "xls"],
        key="gaps_upload"
    )

    if gaps_file:

        metadata, gaps_df = read_gaps_file(
            gaps_file
        )

        if metadata is None or gaps_df is None:

            st.error(
                t(
                    "❌ File missing required rows/columns."
                )
            )

            st.stop()

        st.subheader(
            t("📋 Assessment Information")
        )

        st.markdown(
            f"**{t('👩‍🏫 Teacher:')}** "
            f"{metadata.get('Teacher Name', 'N/A')} | "
            f"**{t('🏫 Class:')}** "
            f"{metadata.get('Class', 'N/A')} | "
            f"**{t('📅 Date:')}** "
            f"{metadata.get('Date', 'N/A')} | "
            f"**{t('📝 Assessment:')}** "
            f"{metadata.get('Assessment name', 'N/A')} | "
            f"**{t('📚 Subject:')}** "
            f"{metadata.get('Subject', 'N/A')}"
        )

        total_students = len(
            gaps_df
        )

        absent_students = int(
            gaps_df["Absent"].sum()
        )

        present_students = (
            total_students
            - absent_students
        )

        absent_percentage = (
            absent_students
            / total_students
            * 100
            if total_students > 0
            else 0
        )

        show_attendance_metrics(
            total_students,
            present_students,
            absent_students,
            round(
                absent_percentage,
                1
            )
        )

        # -----------------------------------------------------
        # Only valid students are used for comparison.
        # -----------------------------------------------------
        gaps_df["Difference"] = (
            gaps_df["Pct2"]
            - gaps_df["Pct1"]
        ).round(1)

        gaps_df["Status"] = gaps_df[
            "Difference"
        ].apply(
            lambda difference:
                t("N/A")
                if pd.isna(difference)
                else
                t("Growth")
                if difference > 0.5
                else
                t("Decay")
                if difference < -0.5
                else
                t("Same")
        )

        gaps_df["Support Level"] = gaps_df[
            "Pct2"
        ].apply(
            support_level
        )

        st.subheader(
            t("📊 Comparison Table (Percentage Based)")
        )

        st.dataframe(
            gaps_df.style.map(
                color_cell,
                subset=["Status"]
            ),
            use_container_width=True
        )

        counts = (
            gaps_df[
                gaps_df["Difference"].notna()
            ]["Status"]
            .value_counts()
            .to_dict()
        )

        growth_count = counts.get(
            t("Growth"),
            0
        )

        decay_count = counts.get(
            t("Decay"),
            0
        )

        same_count = counts.get(
            t("Same"),
            0
        )

        st.subheader(
            t("📢 Summary")
        )

        mc1, mc2, mc3 = st.columns(3)

        mc1.metric(
            f"🟩 {t('Growth')}",
            growth_count
        )

        mc2.metric(
            f"🟥 {t('Decay')}",
            decay_count
        )

        mc3.metric(
            f"🟨 {t('Same')}",
            same_count
        )

        status_df = pd.DataFrame({
            "Status": [
                t("Growth"),
                t("Decay"),
                t("Same")
            ],
            "Count": [
                growth_count,
                decay_count,
                same_count
            ]
        })

        v1, v2 = st.columns(2)

        with v1:

            st.markdown(
                f"**{t('Bar Chart')}**"
            )

            bar_fig = px.bar(
                status_df,
                x="Status",
                y="Count",
                color="Status",
                color_discrete_map={
                    t("Growth"): "green",
                    t("Decay"): "red",
                    t("Same"): "yellow"
                }
            )

            st.plotly_chart(
                bar_fig,
                use_container_width=True
            )

        with v2:

            st.markdown(
                f"**{t('Pie Chart')}**"
            )

            pie_fig = px.pie(
                status_df,
                names="Status",
                values="Count",
                color="Status",
                color_discrete_map={
                    t("Growth"): "green",
                    t("Decay"): "red",
                    t("Same"): "yellow"
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

        st.subheader(
            t("📈 Student Gap (Difference)")
        )

        gap_fig = px.bar(
            gaps_df[
                gaps_df["Difference"].notna()
            ],
            x="Student Name",
            y="Difference",
            color="Status"
        )

        st.plotly_chart(
            gap_fig,
            use_container_width=True
        )

        support_count = (
            gaps_df[
                gaps_df["Pct2"].notna()
            ]["Support Level"]
            .value_counts()
            .reset_index()
        )

        support_count.columns = [
            t("Support Level"),
            t("Students")
        ]

        st.subheader(
            t("👥 Support Groups")
        )

        st.dataframe(
            support_count,
            use_container_width=True
        )

        comparison_buffer = io.BytesIO()

        gaps_df.to_excel(
            comparison_buffer,
            index=False
        )

        st.download_button(
            t("📊 Download Comparison Excel"),
            comparison_buffer.getvalue(),
            "Internal_MAP_Comparison.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# REPORTS
# =========================================================
elif page == "📑 Reports":

    st.title(
        t("📑 Reports")
    )

    st.markdown(
        f"### 🛠️ {t('Available Services')}"
    )

    service = st.radio(
        t("Select Service"),
        [
            t("Compare between sections")
        ]
    )

    if service == t(
        "Compare between sections"
    ):

        st.header(
            t("🔍 Compare Between Sections")
        )

        comp_type = st.radio(
            t("Comparison Type"),
            [
                t("By Assessment Objectives"),
                t("By Assessment Total Mark"),
                t("By External Benchmark Assessment")
            ]
        )

        # =====================================================
        # BY ASSESSMENT OBJECTIVES
        # =====================================================
        if comp_type == t(
            "By Assessment Objectives"
        ):

            st.subheader(
                t("📚 By Assessment Objectives")
            )

            st.info(
                t(
                    "Select number of classes, then upload one Objective Analysis Excel file per class. "
                    "Bands: Below 60% (Weak), 60-75% (Acceptable), "
                    "76-85% (Very Good), 86-100% (Excellent)."
                )
            )

            n_sec = st.number_input(
                t("Number of classes"),
                min_value=2,
                max_value=10,
                value=2,
                step=1,
                key="nsec"
            )

            sec_files = []

            for i in range(
                int(n_sec)
            ):

                sec_files.append(
                    st.file_uploader(
                        f"📄 Class {i+1} file",
                        type=["xlsx", "xls"],
                        key=f"secfile_{i}"
                    )
                )

            if all(sec_files):

                sections_data = []

                for idx, f in enumerate(
                    sec_files,
                    1
                ):

                    meta, df, obj_names, obj_max, obj_desc = read_section_file(
                        f
                    )

                    if meta is None:

                        st.error(
                            f"❌ Class {idx} file invalid"
                        )

                        st.stop()

                    class_name = meta.get(
                        "Class",
                        f"Class {idx}"
                    )

                    st.markdown(
                        f"### 📋 "
                        f"{t('Class')} {idx} "
                        f"{t('Info')}"
                    )

                    m1, m2, m3, m4 = st.columns(4)

                    m1.markdown(
                        f"**{t('👩‍🏫 Teacher:')}** "
                        f"{meta.get('Teacher Name', 'N/A')}"
                    )

                    m2.markdown(
                        f"**{t('🏫 Class:')}** "
                        f"{class_name}"
                    )

                    m3.markdown(
                        f"**{t('📅 Date:')}** "
                        f"{meta.get('Date', 'N/A')}"
                    )

                    m4.markdown(
                        f"**{t('📝 Assessment:')}** "
                        f"{meta.get('Assessment name', 'N/A')}"
                    )

                    st.markdown(
                        f"**{t('📚 Subject:')}** "
                        f"{meta.get('Subject', 'N/A')}"
                    )

                    st.markdown(
                        f"**{t('📚 Objectives:')}**"
                    )

                    for c in obj_names:

                        st.markdown(
                            f"- **{c}** – "
                            f"{obj_desc.get(c, c)}"
                        )

                    # -------------------------------------------------
                    # ATTENDANCE FOR THIS CLASS
                    # -------------------------------------------------
                    total_class_students = len(
                        df
                    )

                    absent_class_students = int(
                        df["Absent"].sum()
                    )

                    present_class_students = (
                        total_class_students
                        - absent_class_students
                    )

                    absent_class_percentage = (
                        absent_class_students
                        / total_class_students
                        * 100
                        if total_class_students > 0
                        else 0
                    )

                    show_attendance_metrics(
                        total_class_students,
                        present_class_students,
                        absent_class_students,
                        round(
                            absent_class_percentage,
                            1
                        )
                    )

                    def band(p):

                        if pd.isna(p):
                            return t(
                                "Below 60% (Weak)"
                            )

                        if p < 60:
                            return t(
                                "Below 60% (Weak)"
                            )

                        elif p <= 75:
                            return t(
                                "60-75% (Acceptable)"
                            )

                        elif p <= 85:
                            return t(
                                "76-85% (Very Good)"
                            )

                        else:
                            return t(
                                "86-100% (Excellent)"
                            )

                    # -------------------------------------------------
                    # ABSENT STUDENTS HAVE NO BAND
                    # -------------------------------------------------
                    df["Band"] = df[
                        "Pct"
                    ].apply(
                        band
                    )

                    obj_avg = {}

                    for c in obj_names:

                        mx = obj_max[c]

                        if mx > 0:

                            valid_objective_scores = (
                                df.loc[
                                    ~df["Absent"],
                                    c
                                ]
                            )

                            obj_avg[c] = (
                                valid_objective_scores
                                / mx
                                * 100
                            ).mean(
                                skipna=True
                            )

                        else:
                            obj_avg[c] = 0

                    sections_data.append({
                        "name":
                            class_name,
                        "df":
                            df,
                        "bands":
                            df[
                                ~df["Absent"]
                            ]["Band"]
                            .value_counts(),
                        "obj_avg":
                            obj_avg,
                        "obj_names":
                            obj_names,
                        "obj_desc":
                            obj_desc
                    })

                band_order = [
                    t("Below 60% (Weak)"),
                    t("60-75% (Acceptable)"),
                    t("76-85% (Very Good)"),
                    t("86-100% (Excellent)")
                ]

                band_df = pd.DataFrame()

                for sd in sections_data:

                    temp = (
                        sd["bands"]
                        .reindex(
                            band_order
                        )
                        .fillna(0)
                        .astype(int)
                    )

                    temp.name = sd["name"]

                    band_df = pd.concat(
                        [
                            band_df,
                            temp.to_frame().T
                        ],
                        axis=0
                    )

                band_df = band_df[
                    band_order
                ]

                plot_df = (
                    band_df
                    .reset_index()
                    .melt(
                        id_vars="index",
                        value_vars=band_order
                    )
                )

                plot_df.columns = [
                    "Class",
                    "Band",
                    "Count"
                ]

                st.subheader(
                    t("📊 Band Distribution per Class")
                )

                st.plotly_chart(
                    px.bar(
                        plot_df,
                        x="Band",
                        y="Count",
                        color="Class",
                        barmode="group",
                        text="Count"
                    ),
                    use_container_width=True
                )

                st.subheader(
                    t(
                        "📈 Dumbbell Chart (Class gap per Band)"
                    )
                )

                fig = go.Figure()

                for sec in band_df.index:

                    fig.add_trace(
                        go.Scatter(
                            x=band_df.loc[sec],
                            y=band_order,
                            mode="markers",
                            name=sec,
                            marker=dict(
                                size=14
                            )
                        )
                    )

                for band in band_order:

                    fig.add_trace(
                        go.Scatter(
                            x=band_df[band].values,
                            y=[band] * len(band_df),
                            mode="lines",
                            line=dict(
                                color="lightgray",
                                width=2
                            ),
                            showlegend=False
                        )
                    )

                fig.update_layout(
                    xaxis_title=t(
                        "Student Count"
                    ),
                    yaxis_title=t(
                        "Performance Band"
                    ),
                    height=400
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.subheader(
                    t(
                        "🏆 Class Order per Objective (Rank 1 = Highest Average %)"
                    )
                )

                rank_rows = []

                obj_union = sections_data[
                    0
                ]["obj_names"]

                for obj in obj_union:

                    avgs = {
                        sd["name"]:
                            sd["obj_avg"].get(
                                obj,
                                0
                            )
                        for sd in sections_data
                    }

                    sorted_secs = sorted(
                        avgs.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )

                    row = {
                        "Objective":
                            obj,
                        "Description":
                            sections_data[
                                0
                            ]["obj_desc"].get(
                                obj,
                                ""
                            )
                    }

                    for i, (
                        sname,
                        val
                    ) in enumerate(
                        sorted_secs,
                        1
                    ):

                        row[
                            f"Rank {i}"
                        ] = (
                            f"{sname} "
                            f"({val:.1f}%)"
                        )

                    rank_rows.append(
                        row
                    )

                rank_df = pd.DataFrame(
                    rank_rows
                )

                st.dataframe(
                    rank_df,
                    use_container_width=True
                )

                st.success(
                    t(
                        "✅ Comparison complete."
                    )
                )

        # =====================================================
        # BY ASSESSMENT TOTAL MARK
        # =====================================================
        elif comp_type == t(
            "By Assessment Total Mark"
        ):

            st.subheader(
                t(
                    "📊 By Assessment Total Mark"
                )
            )

            st.info(
                "Upload Objective Analysis (objectives) OR Total Mark sheets per class. "
                "All will be converted to percentage. "
                "Bands: Below 60% (Weak), 60-75% (Acceptable), "
                "76-85% (Very Good), 86-100% (Excellent)."
            )

            n_sec = st.number_input(
                t("Number of classes"),
                min_value=2,
                max_value=10,
                value=2,
                step=1,
                key="nsec_total"
            )

            sec_files = []

            for i in range(
                int(n_sec)
            ):

                sec_files.append(
                    st.file_uploader(
                        f"📄 Class {i+1} file",
                        type=["xlsx", "xls"],
                        key=f"totalfile_{i}"
                    )
                )

            if all(sec_files):

                sections_data = []

                for idx, f in enumerate(
                    sec_files,
                    1
                ):

                    f.seek(0)

                    raw_check = pd.read_excel(
                        f,
                        header=1
                    )

                    has_total_row = (
                        raw_check.iloc[:, 0]
                        .astype(str)
                        .str.contains(
                            "Points for Objectives",
                            case=False,
                            na=False
                        )
                        .any()
                    )

                    if has_total_row:

                        meta, df = read_objectives_file(
                            f
                        )

                    else:

                        meta, df = read_total_file(
                            f
                        )

                    if meta is None:

                        st.error(
                            f"❌ Class {idx} file invalid (no Pct or Total)"
                        )

                        st.stop()

                    class_name = meta.get(
                        "Class",
                        f"Class {idx}"
                    )

                    st.markdown(
                        f"### 📋 "
                        f"{t('Class')} {idx} "
                        f"{t('Info')}"
                    )

                    m1, m2, m3, m4 = st.columns(4)

                    m1.markdown(
                        f"**{t('👩‍🏫 Teacher:')}** "
                        f"{meta.get('Teacher Name', 'N/A')}"
                    )

                    m2.markdown(
                        f"**{t('🏫 Class:')}** "
                        f"{class_name}"
                    )

                    m3.markdown(
                        f"**{t('📅 Date:')}** "
                        f"{meta.get('Date', 'N/A')}"
                    )

                    m4.markdown(
                        f"**{t('📝 Assessment:')}** "
                        f"{meta.get('Assessment name', 'N/A')}"
                    )

                    st.markdown(
                        f"**{t('📚 Subject:')}** "
                        f"{meta.get('Subject', 'N/A')}"
                    )

                    # Attendance
                    total_class_students = len(
                        df
                    )

                    absent_class_students = int(
                        df["Absent"].sum()
                    )

                    present_class_students = (
                        total_class_students
                        - absent_class_students
                    )

                    absent_class_percentage = (
                        absent_class_students
                        / total_class_students
                        * 100
                        if total_class_students > 0
                        else 0
                    )

                    show_attendance_metrics(
                        total_class_students,
                        present_class_students,
                        absent_class_students,
                        round(
                            absent_class_percentage,
                            1
                        )
                    )

                    def band(p):

                        if pd.isna(p):
                            return t(
                                "Below 60% (Weak)"
                            )

                        if p < 60:
                            return t(
                                "Below 60% (Weak)"
                            )

                        elif p <= 75:
                            return t(
                                "60-75% (Acceptable)"
                            )

                        elif p <= 85:
                            return t(
                                "76-85% (Very Good)"
                            )

                        else:
                            return t(
                                "86-100% (Excellent)"
                            )

                    df["Band"] = df[
                        "Pct"
                    ].apply(
                        band
                    )

                    sections_data.append({
                        "name":
                            class_name,
                        "df":
                            df,
                        "bands":
                            df[
                                ~df["Absent"]
                            ]["Band"]
                            .value_counts()
                    })

                band_order = [
                    t("Below 60% (Weak)"),
                    t("60-75% (Acceptable)"),
                    t("76-85% (Very Good)"),
                    t("86-100% (Excellent)")
                ]

                band_df = pd.DataFrame()

                for sd in sections_data:

                    temp = (
                        sd["bands"]
                        .reindex(
                            band_order
                        )
                        .fillna(0)
                        .astype(int)
                    )

                    temp.name = sd["name"]

                    band_df = pd.concat(
                        [
                            band_df,
                            temp.to_frame().T
                        ],
                        axis=0
                    )

                band_df = band_df[
                    band_order
                ]

                plot_df = (
                    band_df
                    .reset_index()
                    .melt(
                        id_vars="index",
                        value_vars=band_order
                    )
                )

                plot_df.columns = [
                    "Class",
                    "Band",
                    "Count"
                ]

                st.subheader(
                    t(
                        "📊 Band Distribution per Class"
                    )
                )

                st.plotly_chart(
                    px.bar(
                        plot_df,
                        x="Band",
                        y="Count",
                        color="Class",
                        barmode="group",
                        text="Count"
                    ),
                    use_container_width=True
                )

                st.subheader(
                    t(
                        "📈 Dumbbell Chart (Class gap per Band)"
                    )
                )

                fig = go.Figure()

                for sec in band_df.index:

                    fig.add_trace(
                        go.Scatter(
                            x=band_df.loc[sec],
                            y=band_order,
                            mode="markers",
                            name=sec,
                            marker=dict(
                                size=14
                            )
                        )
                    )

                for band in band_order:

                    fig.add_trace(
                        go.Scatter(
                            x=band_df[band].values,
                            y=[band] * len(band_df),
                            mode="lines",
                            line=dict(
                                color="lightgray",
                                width=2
                            ),
                            showlegend=False
                        )
                    )

                fig.update_layout(
                    xaxis_title=t(
                        "Student Count"
                    ),
                    yaxis_title=t(
                        "Performance Band"
                    ),
                    height=400
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.success(
                    "✅ Total Mark comparison complete."
                )

        # =====================================================
        # EXTERNAL BENCHMARK
        # =====================================================
        elif comp_type == t(
            "By External Benchmark Assessment"
        ):

            st.subheader(
                t(
                    "🏢 By External Benchmark Assessment"
                )
            )

            st.info(
                "Upload External Benchmark (objectives or total) sheets per class. "
                "All will be converted to percentage. "
                "Bands: Below 60% (Weak), 60-75% (Acceptable), "
                "76-85% (Very Good), 86-100% (Excellent)."
            )

            n_sec = st.number_input(
                t("Number of classes"),
                min_value=2,
                max_value=10,
                value=2,
                step=1,
                key="nsec_ext"
            )

            sec_files = []

            for i in range(
                int(n_sec)
            ):

                sec_files.append(
                    st.file_uploader(
                        f"📄 Class {i+1} file",
                        type=["xlsx", "xls"],
                        key=f"extfile_{i}"
                    )
                )

            if all(sec_files):

                sections_data = []

                for idx, f in enumerate(
                    sec_files,
                    1
                ):

                    f.seek(0)

                    raw_check = pd.read_excel(
                        f,
                        header=1
                    )

                    has_total_row = (
                        raw_check.iloc[:, 0]
                        .astype(str)
                        .str.contains(
                            "Points for Objectives",
                            case=False,
                            na=False
                        )
                        .any()
                    )

                    if has_total_row:

                        meta, df = read_objectives_file(
                            f
                        )

                    else:

                        meta, df = read_total_file(
                            f
                        )

                    if meta is None:

                        st.error(
                            f"❌ Class {idx} file invalid (no Pct or Total)"
                        )

                        st.stop()

                    class_name = meta.get(
                        "Class",
                        f"Class {idx}"
                    )

                    st.markdown(
                        f"### 📋 "
                        f"{t('Class')} {idx} "
                        f"{t('Info')}"
                    )

                    m1, m2, m3, m4 = st.columns(4)

                    m1.markdown(
                        f"**{t('👩‍🏫 Teacher:')}** "
                        f"{meta.get('Teacher Name', 'N/A')}"
                    )

                    m2.markdown(
                        f"**{t('🏫 Class:')}** "
                        f"{class_name}"
                    )

                    m3.markdown(
                        f"**{t('📅 Date:')}** "
                        f"{meta.get('Date', 'N/A')}"
                    )

                    m4.markdown(
                        f"**{t('📝 Assessment:')}** "
                        f"{meta.get('Assessment name', 'N/A')}"
                    )

                    st.markdown(
                        f"**{t('📚 Subject:')}** "
                        f"{meta.get('Subject', 'N/A')}"
                    )

                    total_class_students = len(
                        df
                    )

                    absent_class_students = int(
                        df["Absent"].sum()
                    )

                    present_class_students = (
                        total_class_students
                        - absent_class_students
                    )

                    absent_class_percentage = (
                        absent_class_students
                        / total_class_students
                        * 100
                        if total_class_students > 0
                        else 0
                    )

                    show_attendance_metrics(
                        total_class_students,
                        present_class_students,
                        absent_class_students,
                        round(
                            absent_class_percentage,
                            1
                        )
                    )

                    def band(p):

                        if pd.isna(p):
                            return t(
                                "Below 60% (Weak)"
                            )

                        if p < 60:
                            return t(
                                "Below 60% (Weak)"
                            )

                        elif p <= 75:
                            return t(
                                "60-75% (Acceptable)"
                            )

                        elif p <= 85:
                            return t(
                                "76-85% (Very Good)"
                            )

                        else:
                            return t(
                                "86-100% (Excellent)"
                            )

                    df["Band"] = df[
                        "Pct"
                    ].apply(
                        band
                    )

                    sections_data.append({
                        "name":
                            class_name,
                        "df":
                            df,
                        "bands":
                            df[
                                ~df["Absent"]
                            ]["Band"]
                            .value_counts()
                    })

                band_order = [
                    t("Below 60% (Weak)"),
                    t("60-75% (Acceptable)"),
                    t("76-85% (Very Good)"),
                    t("86-100% (Excellent)")
                ]

                band_df = pd.DataFrame()

                for sd in sections_data:

                    temp = (
                        sd["bands"]
                        .reindex(
                            band_order
                        )
                        .fillna(0)
                        .astype(int)
                    )

                    temp.name = sd["name"]

                    band_df = pd.concat(
                        [
                            band_df,
                            temp.to_frame().T
                        ],
                        axis=0
                    )

                band_df = band_df[
                    band_order
                ]

                plot_df = (
                    band_df
                    .reset_index()
                    .melt(
                        id_vars="index",
                        value_vars=band_order
                    )
                )

                plot_df.columns = [
                    "Class",
                    "Band",
                    "Count"
                ]

                st.subheader(
                    t(
                        "📊 Band Distribution per Class"
                    )
                )

                st.plotly_chart(
                    px.bar(
                        plot_df,
                        x="Band",
                        y="Count",
                        color="Class",
                        barmode="group",
                        text="Count"
                    ),
                    use_container_width=True
                )

                st.subheader(
                    t(
                        "📈 Dumbbell Chart (Class gap per Band)"
                    )
                )

                fig = go.Figure()

                for sec in band_df.index:

                    fig.add_trace(
                        go.Scatter(
                            x=band_df.loc[sec],
                            y=band_order,
                            mode="markers",
                            name=sec,
                            marker=dict(
                                size=14
                            )
                        )
                    )

                for band in band_order:

                    fig.add_trace(
                        go.Scatter(
                            x=band_df[band].values,
                            y=[band] * len(band_df),
                            mode="lines",
                            line=dict(
                                color="lightgray",
                                width=2
                            ),
                            showlegend=False
                        )
                    )

                fig.update_layout(
                    xaxis_title=t(
                        "Student Count"
                    ),
                    yaxis_title=t(
                        "Performance Band"
                    ),
                    height=400
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.success(
                    "✅ External Benchmark comparison complete."
                )

