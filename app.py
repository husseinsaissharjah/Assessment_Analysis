import streamlit as st
import pandas as pd
import plotly.express as px
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

        # Levels
        "Absent": "غائب",
        "Fail": "راسب",
        "Acceptable": "مقبول",
        "Good": "جيد",
        "Excellent": "ممتاز",

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
        "76-84% (Good)": "76-84% (جيد)",
        "85-100% (Excellent)": "85-100% (ممتاز)",
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
        "✅ Comparison complete.": "✅ اكتملت المقارنة.",
        "📊 By Assessment Total Mark": "📊 حسب الدرجة الإجمالية للتقييم",
        "🏢 By External Benchmark Assessment": "🏢 حسب تقييم المعيار الخارجي",

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

        if st.button(
            btn_label,
            key=f"navigation_{p}",
            use_container_width=True
        ):
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
    "Excellent": "#9467bd"
}

ORDER = [
    "Absent",
    "Fail",
    "Acceptable",
    "Good",
    "Excellent"
]

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
            "",
            "Fractions",
            "Algebra",
            "Geometry",
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

    return save_workbook_to_bytes(data)


def total_template():
    data = [
        [
            "Teacher Name: Example Teacher",
            "Class: Grade 7A",
            "Date: 27/08/2026",
            "Assessment name: Internal Assessment",
            "Subject: Mathematics"
        ],
        ["Student Name", "Total"],
        ["Total", 100],
        ["Student 1", 82],
        ["Student 2", 91],
        ["Student 3", 65]
    ]

    return save_workbook_to_bytes(data)


def gaps_template():
    data = [
        [
            "Teacher Name: Example Teacher",
            "Class: Grade 7A",
            "Date: 27/08/2026",
            "Assessment name: Internal vs MAP",
            "Subject: Mathematics"
        ],
        ["Student Name", "Total of Internal", "Percentile of MAP"],
        ["Over", 100, ""],
        ["Student 1", 82, 75],
        ["Student 2", 91, 88],
        ["Student 3", 65, 50]
    ]

    return save_workbook_to_bytes(data)


def map_template():
    data = {
        "Student Name": [
            "Student 1",
            "Student 2",
            "Student 3",
            "Student 4"
        ],
        "Grade": [7, 7, 7, 7],
        "Subject": [
            "Mathematics",
            "Mathematics",
            "Mathematics",
            "Mathematics"
        ],
        "Previous RIT": [205, 210, 198, 215],
        "Current RIT": [210, 214, 200, 218],
        "Percentile": [55, 70, 40, 85]
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
# READ OBJECTIVES FILE
# =========================================================
def read_objectives_file(file):
    try:
        file.seek(0)

        meta_raw = pd.read_excel(
            file,
            nrows=1,
            header=None
        )

        meta = {}

        for value in meta_raw.iloc[0].tolist():
            text = str(value).strip()

            if ":" in text:
                key, value_part = text.split(":", 1)
                meta[key.strip()] = value_part.strip()

        file.seek(0)

        df = pd.read_excel(
            file,
            header=1
        )

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

        df = df[~mask].copy()

        df = df.rename(
            columns={first_col: "Student Name"}
        )

        df = df.dropna(
            subset=["Student Name"]
        )

        keep_columns = ["Student Name"] + valid_cols

        df = df[keep_columns].copy()

        # IMPORTANT:
        # Do not convert missing/absent marks to zero here.
        # We preserve missing values so absent students
        # can be identified correctly.
        for column in valid_cols:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # Calculate total only for available numeric marks.
        df["Obtained"] = df[valid_cols].sum(
            axis=1,
            min_count=1
        )

        df["Pct"] = (
            df["Obtained"] / total_max * 100
        ).round(1)

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
            if "total" in str(raw.iloc[i, 0]).lower():
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
            .str.contains("total", na=False)
        ]

        data = data.rename(
            columns={data.columns[0]: "Student Name"}
        )

        total_columns = [
            c for c in data.columns
            if "total" in str(c).lower()
        ]

        if not total_columns:
            return None, None

        total_column = total_columns[0]

        data[total_column] = pd.to_numeric(
            data[total_column],
            errors="coerce"
        )

        data["Pct"] = (
            data[total_column] / max_total * 100
        ).round(1)

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
            if "over" in str(raw.iloc[i, 0]).lower():
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
            .str.contains("over", na=False)
        ]

        data = data.rename(
            columns={data.columns[0]: "Student Name"}
        )

        internal_columns = [
            c for c in data.columns
            if "total of internal" in str(c).lower()
        ]

        map_columns = [
            c for c in data.columns
            if "percentile of map" in str(c).lower()
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
            data[internal_column] / max_total * 100
        ).round(1)

        data["Pct2"] = data[map_column].round(1)

        data = data[
            ["Student Name", "Pct1", "Pct2"]
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

        first_value = (
            str(raw_full.iloc[0, 0])
            .strip()
            .lower()
        )

        if first_value != "points for objectives":
            desc_row = raw_full.iloc[0]
        else:
            desc_row = None

        obj_names = [
            c for c in df.columns
            if c not in [
                "Student Name",
                "Obtained",
                "Pct"
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
            max_row = raw_full[points_mask].iloc[0]
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
            "Analyze MAP, internal assessments, grades, "
            "and student performance in seconds."
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
            "Use the sidebar on the left to navigate "
            "to your analysis."
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
            "The Assessment Analysis tool is designed to help "
            "teachers, coordinators, and school leaders analyze "
            "student achievement quickly and consistently."
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
                "Analyze one assessment at a time using "
                "learning objectives and student marks."
            )
        )

    with c2:
        st.subheader(
            t("📈 Class Total Average Analysis")
        )

        st.write(
            t(
                "Compare multiple assessments for the same "
                "class and monitor the class average progress "
                "over time."
            )
        )

    with c3:
        st.subheader(
            t("🎯 Achievement & Gaps")
        )

        st.write(
            t(
                "Compare Internal Assessment results with "
                "MAP Percentile in one sheet to identify "
                "achievement gaps."
            )
        )

    st.markdown("---")

    st.subheader(
        t("🗺️ MAP Analysis")
    )

    st.write(
        t(
            "The MAP Analysis section allows you to compare "
            "previous and current RIT scores, growth, and "
            "percentile performance."
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
            "Analyze a single assessment based on learning "
            "objectives and student marks."
        )
    )

    st.download_button(
        t("📥 Download Excel Template"),
        objectives_template(),
        "Student_Analysis_Template.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
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

        first_value = (
            str(raw.iloc[0, 0])
            .strip()
            .lower()
        )

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

        max_row = raw_students[mask].iloc[0]

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

        student_df = (
            raw_students[~mask]
            .copy()
            .dropna(subset=[first_column])
        )

        student_df = student_df.rename(
            columns={first_column: "Student Name"}
        )

        student_df = student_df[
            ["Student Name"] + obj_names
        ].copy()

        # =====================================================
        # ABSENT STUDENT DETECTION
        # =====================================================
        def is_absent(row):

            has_a = False
            all_empty = True

            for column in obj_names:

                value = row[column]

                if isinstance(value, str):

                    text = value.strip().lower()

                    if (
                        text == "a"
                        or text == "absent"
                    ):
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

        # Convert numeric marks.
        # Absent marks remain NaN and are NOT converted to zero.
        for column in obj_names:

            student_df[column] = pd.to_numeric(
                student_df[column],
                errors="coerce"
            )

        total_max = sum(obj_max)

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

        # =====================================================
        # DATA VALIDATION
        # =====================================================
        errors = []

        for _, row in student_df.iterrows():

            if row["Absent"]:
                continue

            for index, column in enumerate(
                obj_names
            ):

                value = row[column]

                if pd.isna(value):
                    continue

                value = float(value)

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

                # =================================================
                # STUDENT ANALYSIS
                # =================================================
                for _, row in student_df.iterrows():

                    # ---------------------------------------------
                    # ABSENT STUDENT
                    # ---------------------------------------------
                    if row["Absent"]:

                        results.append(
                            {
                                "Student Name":
                                    row["Student Name"],
                                "Total": "-",
                                "Total %": None,
                                "Level":
                                    t("Absent")
                            }
                        )

                        continue

                    # ---------------------------------------------
                    # CALCULATE PERCENTAGE
                    # ---------------------------------------------
                    total_obtained = 0.0
                    total_possible_for_student = 0.0

                    for index, column in enumerate(
                        obj_names
                    ):

                        mark = row[column]

                        # Ignore missing objective marks.
                        if pd.isna(mark):
                            continue

                        mark = float(mark)

                        total_obtained += mark
                        total_possible_for_student += (
                            obj_max[index]
                        )

                    if total_possible_for_student > 0:

                        total_percentage = (
                            total_obtained
                            / total_possible_for_student
                            * 100
                        )

                    else:
                        total_percentage = None

                    # ---------------------------------------------
                    # ACHIEVEMENT LEVELS
                    #
                    # < 60%       = Fail
                    # 60% - 75%   = Acceptable
                    # 76% - 84%   = Good
                    # 85%+        = Excellent
                    # ---------------------------------------------
                    if total_percentage is None:

                        level = t("N/A")

                    elif total_percentage < 60:

                        level = t("Fail")

                    elif total_percentage <= 75:

                        level = t("Acceptable")

                    elif total_percentage <= 84:

                        level = t("Good")

                    else:

                        level = t("Excellent")

                    results.append(
                        {
                            "Student Name":
                                row["Student Name"],
                            "Total":
                                round(
                                    total_obtained,
                                    1
                                ),
                            "Total %":
                                round(
                                    total_percentage,
                                    1
                                )
                                if total_percentage is not None
                                else None,
                            "Level":
                                level
                        }
                    )

                rdf = pd.DataFrame(results)

                rdf["Support Level"] = (
                    rdf["Total %"]
                    .apply(support_level)
                )

                st.header(
                    t("Step 2: Analysis Report")
                )

                # =================================================
                # LEVEL COUNTS
                # =================================================
                counts = (
                    rdf["Level"]
                    .value_counts()
                    .to_dict()
                )

                # =================================================
                # ACHIEVEMENT METRICS
                # =================================================
                c1, c2, c3, c4, c5 = st.columns(5)

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
                    t("Excellent"),
                    counts.get(
                        t("Excellent"),
                        0
                    )
                )

                # =================================================
                # VALID STUDENTS ONLY
                # ABSENT STUDENTS ARE EXCLUDED
                # =================================================
                valid_percentages = (
                    rdf["Total %"]
                    .dropna()
                )

                total_students = len(
                    valid_percentages
                )

                # =================================================
                # CLASS ACHIEVEMENT DISTRIBUTION
                # =================================================
                if total_students > 0:

                    fail_percentage = (
                        (
                            valid_percentages < 60
                        ).sum()
                        / total_students
                        * 100
                    )

                    acceptable_percentage = (
                        (
                            (
                                valid_percentages >= 60
                            )
                            &
                            (
                                valid_percentages <= 75
                            )
                        ).sum()
                        / total_students
                        * 100
                    )

                    good_percentage = (
                        (
                            (
                                valid_percentages >= 76
                            )
                            &
                            (
                                valid_percentages <= 84
                            )
                        ).sum()
                        / total_students
                        * 100
                    )

                    excellent_percentage = (
                        (
                            valid_percentages >= 85
                        ).sum()
                        / total_students
                        * 100
                    )

                else:

                    fail_percentage = 0
                    acceptable_percentage = 0
                    good_percentage = 0
                    excellent_percentage = 0

                # =================================================
                # OVERALL CLASS JUDGMENT
                # =================================================
                if total_students == 0:

                    overall = t("N/A")

                elif excellent_percentage >= 90:

                    overall = t("Excellent")

                elif (
                    good_percentage
                    + excellent_percentage
                ) >= 75:

                    overall = t("Good")

                elif (
                    acceptable_percentage
                    + good_percentage
                    + excellent_percentage
                ) >= 60:

                    overall = t("Acceptable")

                else:

                    overall = t("Below Acceptable")

                # =================================================
                # SUMMARY
                # =================================================
                st.subheader(
                    t("📢 Summary")
                )

                st.success(
                    f"**{overall}**"
                )

                s1, s2, s3, s4 = st.columns(4)

                s1.metric(
                    t("Fail"),
                    f"{fail_percentage:.1f}%"
                )

                s2.metric(
                    t("Acceptable"),
                    f"{acceptable_percentage:.1f}%"
                )

                s3.metric(
                    t("Good"),
                    f"{good_percentage:.1f}%"
                )

                s4.metric(
                    t("Excellent"),
                    f"{excellent_percentage:.1f}%"
                )

            # =================================================
# LEVEL DISTRIBUTION
# ABSENT STUDENTS ARE EXCLUDED FROM PIE CHART
# =================================================
level_df = (
    rdf[
        rdf["Level"] != t("Absent")
    ]["Level"]
    .value_counts()
    .reset_index()
)

level_df.columns = [
    "Level",
    "Count"
]

ordered_levels = [
    t("Fail"),
    t("Acceptable"),
    t("Good"),
    t("Excellent")
]

level_df["Level"] = pd.Categorical(
    level_df["Level"],
    categories=ordered_levels,
    ordered=True
)

level_df = (
    level_df
    .sort_values("Level")
)
                )

                v1, v2 = st.columns(2)

                # =================================================
                # STUDENT ACHIEVEMENT CHART
                # =================================================
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
                        range_y=[0, 100],
                        color_discrete_map={
                            t(key): value
                            for key, value
                            in COLORS.items()
                        }
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                # =================================================
                # LEVEL DISTRIBUTION PIE CHART
                # =================================================
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

                # =================================================
                # SUPPORT LEVELS
                # =================================================
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

                support_count = (
                    rdf["Support Level"]
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

                # =================================================
                # FINAL STUDENT REPORT
                # =================================================
                st.dataframe(
                    rdf,
                    use_container_width=True
                )

                # =================================================
                # DOWNLOAD REPORT
                # =================================================
                excel_buffer = io.BytesIO()

                rdf.to_excel(
                    excel_buffer,
                    index=False
                )

                excel_buffer.seek(0)

                st.download_button(
                    t("📊 Download Excel"),
                    excel_buffer.getvalue(),
                    "Report.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
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
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    st.info(
        t(
            "Choose the number of assessments. Upload files "
            "using the same Excel format as Objective Analysis."
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

        for index, file in enumerate(
            assessment_files
        ):

            meta, df = read_objectives_file(
                file
            )

            if meta is None or df is None:

                st.error(
                    t(
                        "❌ File missing "
                        "'Points for Objectives' row."
                    )
                )

                st.stop()

            metadata_list.append(meta)

            percentage_column = (
                f"Pct{index + 1}"
            )

            keep = (
                df[
                    ["Student Name", "Pct"]
                ]
                .rename(
                    columns={
                        "Pct":
                            percentage_column
                    }
                )
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

        merged[
            percentage_columns
        ] = merged[
            percentage_columns
        ].fillna(0)

        merged["Difference"] = (
            merged[
                percentage_columns[-1]
            ]
            -
            merged[
                percentage_columns[0]
            ]
        ).round(1)

        merged["Status"] = (
            merged["Difference"]
            .apply(
                lambda difference:
                    t("Growth")
                    if difference > 0.5
                    else
                    t("Decay")
                    if difference < -0.5
                    else
                    t("Same")
            )
        )

        merged["Support Level"] = (
            merged[
                percentage_columns[-1]
            ]
            .apply(support_level)
        )

        st.subheader(
            t(
                "📊 Comparison Table "
                "(Percentage Based)"
            )
        )

        st.dataframe(
            merged.style.map(
                color_cell,
                subset=["Status"]
            ),
            use_container_width=True
        )

        status_counts = (
            merged["Status"]
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

        status_df = pd.DataFrame(
            {
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
            }
        )

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

        average_data = (
            merged[
                percentage_columns
            ]
            .mean()
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
            merged,
            x="Student Name",
            y="Difference",
            color="Status"
        )

        st.plotly_chart(
            growth_fig,
            use_container_width=True
        )

        support_count = (
            merged["Support Level"]
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

        comparison_buffer.seek(0)

        st.download_button(
            t("📊 Download Comparison Excel"),
            comparison_buffer.getvalue(),
            "Comparison.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
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
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
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
                    + ", ".join(missing_columns)
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

            map_df["RIT Growth"] = (
                map_df["Current RIT"]
                -
                map_df["Previous RIT"]
            )

            map_df["Growth Status"] = (
                map_df["RIT Growth"]
                .apply(
                    lambda value:
                        t("Growth")
                        if value > 0
                        else
                        t("Decay")
                        if value < 0
                        else
                        t("Same")
                )
            )

            map_df["Support Level"] = (
                map_df["Percentile"]
                .apply(support_level)
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

            average_previous = (
                map_df["Previous RIT"]
                .mean()
            )

            average_current = (
                map_df["Current RIT"]
                .mean()
            )

            average_growth = (
                map_df["RIT Growth"]
                .mean()
            )

            average_percentile = (
                map_df["Percentile"]
                .mean()
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

            st.markdown("---")

            status_count = (
                map_df["Growth Status"]
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
                    map_df,
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
                map_df,
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
                map_df["Support Level"]
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

            map_buffer.seek(0)

            st.download_button(
                t("📥 Download MAP Analysis"),
                map_buffer.getvalue(),
                "MAP_Analysis_Report.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
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
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
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

        gaps_df["Difference"] = (
            gaps_df["Pct2"]
            -
            gaps_df["Pct1"]
        ).round(1)

        gaps_df["Status"] = (
            gaps_df["Difference"]
            .apply(
                lambda difference:
                    t("Growth")
                    if difference > 0.5
                    else
                    t("Decay")
                    if difference < -0.5
                    else
                    t("Same")
            )
        )

        gaps_df["Support Level"] = (
            gaps_df["Pct2"]
            .apply(support_level)
        )

        st.subheader(
            t(
                "📊 Comparison Table "
                "(Percentage Based)"
            )
        )

        st.dataframe(
            gaps_df.style.map(
                color_cell,
                subset=["Status"]
            ),
            use_container_width=True
        )

        counts = (
            gaps_df["Status"]
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

        status_df = pd.DataFrame(
            {
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
            }
        )

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
            gaps_df,
            x="Student Name",
            y="Difference",
            color="Status"
        )

        st.plotly_chart(
            gap_fig,
            use_container_width=True
        )

        support_count = (
            gaps_df["Support Level"]
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

        comparison_buffer.seek(0)

        st.download_button(
            t("📊 Download Comparison Excel"),
            comparison_buffer.getvalue(),
            "Internal_MAP_Comparison.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )


# =========================================================
# REPORTS
# =========================================================
elif page == "📑 Reports":

    service = st.radio(
        t("Select Service"),
        [
            t("Compare between sections")
        ],
        key="report_service"
    )

    if service == t(
        "Compare between sections"
    ):

        st.header(
            t("🔍 Compare Between Sections")
        )

        comparison_type = st.radio(
            t("Comparison Type"),
            [
                t("By Assessment Objectives"),
                t("By Assessment Total Mark"),
                t("By External Benchmark Assessment")
            ],
            key="comparison_type"
        )

        # =====================================================
        # OBJECTIVES
        # =====================================================
        if comparison_type == t(
            "By Assessment Objectives"
        ):

            number_of_classes = st.number_input(
                t("Number of classes"),
                min_value=2,
                max_value=10,
                value=2,
                step=1,
                key="number_of_classes"
            )

            section_files = []

            for index in range(
                int(number_of_classes)
            ):

                section_files.append(
                    st.file_uploader(
                        f"📄 {t('Class')} "
                        f"{index + 1} "
                        f"{t('file')}",
                        type=["xlsx", "xls"],
                        key=f"section_file_{index}"
                    )
                )

            if all(section_files):

                sections_data = []

                for index, file in enumerate(
                    section_files,
                    1
                ):

                    (
                        metadata,
                        section_df,
                        objective_names,
                        objective_max,
                        objective_descriptions
                    ) = read_section_file(file)

                    if metadata is None:

                        st.error(
                            t(
                                "❌ Class file invalid"
                            )
                        )

                        st.stop()

                    class_name = metadata.get(
                        "Class",
                        f"{t('Class')} {index}"
                    )

                    st.markdown(
                        f"### 📋 {t('Class')} "
                        f"{index} {t('Info')}"
                    )

                    m1, m2, m3, m4 = st.columns(4)

                    m1.markdown(
                        f"**{t('👩‍🏫 Teacher:')}** "
                        f"{metadata.get('Teacher Name', 'N/A')}"
                    )

                    m2.markdown(
                        f"**{t('🏫 Class:')}** "
                        f"{class_name}"
                    )

                    m3.markdown(
                        f"**{t('📅 Date:')}** "
                        f"{metadata.get('Date', 'N/A')}"
                    )

                    m4.markdown(
                        f"**{t('📝 Assessment:')}** "
                        f"{metadata.get('Assessment name', 'N/A')}"
                    )

                    def calculate_band(
                        percentage
                    ):

                        if pd.isna(percentage):
                            return t(
                                "Below 60% (Weak)"
                            )

                        if percentage < 60:
                            return t(
                                "Below 60% (Weak)"
                            )

                        if percentage <= 75:
                            return t(
                                "60-75% (Acceptable)"
                            )

                        if percentage <= 84:
                            return t(
                                "76-84% (Good)"
                            )

                        return t(
                            "85-100% (Excellent)"
                        )

                    section_df["Band"] = (
                        section_df["Pct"]
                        .apply(calculate_band)
                    )

                    objective_average = {}

                    for objective in objective_names:

                        maximum = objective_max.get(
                            objective,
                            0
                        )

                        if maximum > 0:

                            objective_average[
                                objective
                            ] = (
                                section_df[objective]
                                / maximum
                                * 100
                            ).mean()

                        else:

                            objective_average[
                                objective
                            ] = 0

                    sections_data.append(
                        {
                            "name":
                                class_name,

                            "df":
                                section_df,

                            "bands":
                                section_df[
                                    "Band"
                                ].value_counts(),

                            "obj_avg":
                                objective_average,

                            "obj_names":
                                objective_names,

                            "obj_desc":
                                objective_descriptions
                        }
                    )

                band_order = [
                    t(
                        "Below 60% (Weak)"
                    ),
                    t(
                        "60-75% (Acceptable)"
                    ),
                    t(
                        "76-84% (Good)"
                    ),
                    t(
                        "85-100% (Excellent)"
                    )
                ]

                band_rows = []

                for section in sections_data:

                    counts = (
                        section["bands"]
                        .reindex(band_order)
                        .fillna(0)
                        .astype(int)
                    )

                    row = {
                        t("Class"):
                            section["name"]
                    }

                    for band in band_order:

                        row[band] = counts.get(
                            band,
                            0
                        )

                    band_rows.append(row)

                band_df = pd.DataFrame(
                    band_rows
                )

                plot_df = band_df.melt(
                    id_vars=t("Class"),
                    value_vars=band_order,
                    var_name=t("Band"),
                    value_name=t("Count")
                )

                st.subheader(
                    t(
                        "📊 Band Distribution "
                        "per Class"
                    )
                )

                band_fig = px.bar(
                    plot_df,
                    x=t("Band"),
                    y=t("Count"),
                    color=t("Class"),
                    barmode="group",
                    text=t("Count")
                )

                st.plotly_chart(
                    band_fig,
                    use_container_width=True
                )

                st.success(
                    t(
                        "✅ Comparison complete."
                    )
                )

        # =====================================================
        # TOTAL MARK
        # =====================================================
        elif comparison_type == t(
            "By Assessment Total Mark"
        ):

            st.info(
                t(
                    "This comparison option is ready "
                    "for total-mark based analysis."
                )
            )

        # =====================================================
        # EXTERNAL BENCHMARK
        # =====================================================
        elif comparison_type == t(
            "By External Benchmark Assessment"
        ):

            st.info(
                t(
                    "This comparison option is ready "
                    "for external benchmark analysis."
                )
            )


# =========================================================
# END OF APP
# =========================================================
