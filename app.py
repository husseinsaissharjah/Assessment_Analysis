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
# LANGUAGE & STATE SETUP
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
        "🏠 Home": "🏠 الرئيسية",
        "📊 Overview": "📊 نظرة عامة",
        "📝 Objective Analysis": "📝 تحليل الأهداف",
        "📈 Class Total Average Analysis": "📈 تحليل متوسط الصف",
        "🗺️ MAP Analysis": "🗺️ تحليل ماب",
        "🎯 Achievement & Gaps": "🎯 الإنجاز والفجوات",
        "📑 Reports": "📑 التقارير",
        "Navigation": "التنقل",

        # Home
        "Assessment Analysis": "تحليل التقييم",
        "### Student Assessment & Achievement Dashboard":
            "### لوحة تقييم الطلاب والإنجاز",
        "Analyze MAP, internal assessments, grades, and student performance in seconds.":
            "حلل تقييمات ماب والتقييمات الداخلية والدرجات وأداء الطلاب في ثوانٍ.",
        "### 📌 How to use": "### 📌 كيفية الاستخدام",
        "### ① Upload Data": "### ① تحميل البيانات",
        "Upload your Excel files with student marks.":
            "قم بتحميل ملفات إكسل التي تحتوي على علامات الطلاب.",
        "### ② Choose Analysis": "### ② اختر التحليل",
        "Pick the analysis type from the sidebar.":
            "اختر نوع التحليل من القائمة الجانبية.",
        "### ③ View Insights": "### ③ عرض النتائج",
        "See charts, gaps, and download reports.":
            "شاهد الرسوم البيانية والفجوات وقم بتحميل التقارير.",
        "Use the sidebar on the left to navigate to your analysis.":
            "استخدم القائمة الجانبية للتنقل بين التحليلات.",

        # Overview
        "📊 Assessment Analysis Overview": "📊 نظرة عامة على تحليل التقييم",
        "The Assessment Analysis tool is designed to help teachers, coordinators, and school leaders analyze student achievement quickly and consistently.":
            "صممت أداة تحليل التقييم لمساعدة المعلمين والمنسقين وقادة المدارس على تحليل إنجاز الطلاب بسرعة وبطريقة متسقة.",

        # Analysis
        "📝 Objective Analysis": "📝 تحليل الأهداف",
        "Analyze one assessment at a time using learning objectives and student marks.":
            "حلل تقييماً واحداً في كل مرة باستخدام أهداف التعلم وعلامات الطلاب.",

        "📈 Class Total Average Analysis": "📈 تحليل متوسط الصف",
        "Compare multiple assessments for the same class and monitor the class average progress over time.":
            "قارن بين تقييمات متعددة لنفس الصف وراقب تطور متوسط الصف عبر الوقت.",

        "🗺️ MAP Analysis": "🗺️ تحليل ماب",
        "🎯 Achievement & Gaps": "🎯 الإنجاز والفجوات",
        "Compare Internal Assessment results with MAP Percentile in one sheet to identify achievement gaps.":
            "قارن نتائج التقييم الداخلي مع النسبة المئوية لماب لتحديد فجوات الإنجاز.",

        # Labels
        "👩‍🏫 Teacher:": "👩‍🏫 المعلم:",
        "🏫 Class:": "🏫 الصف:",
        "📅 Date:": "📅 التاريخ:",
        "📝 Assessment:": "📝 التقييم:",
        "📚 Subject:": "📚 المادة:",
        "Subject:": "المادة:",
        "Class": "الصف",
        "Info": "معلومات",
        "Name:": "الاسم:",

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
        "Students": "الطلاب",

        # Bands
        "Below 60% (Weak)": "أقل من 60% (ضعيف)",
        "60-75% (Acceptable)": "60-75% (مقبول)",
        "76-85% (Very Good)": "76-85% (جيد جداً)",
        "86-100% (Excellent)": "86-100% (ممتاز)",

        # Objective Analysis
        "Auto Total Max Mark": "الحد الأقصى للدرجات",
        "Objectives": "الأهداف",
        "Preview": "معاينة",
        "Analyze Assessment": "تحليل التقييم",
        "Step 2: Analysis Report": "الخطوة 2: تقرير التحليل",
        "Step 1: Upload Student Marks Excel":
            "الخطوة 1: تحميل ملف إكسل علامات الطلاب",
        "Upload Excel": "تحميل إكسل",
        "📊 Preview": "📊 معاينة",
        "📊 Student Achievement": "📊 إنجاز الطالب",
        "📊 Level Distribution": "📊 توزيع المستويات",
        "🎯 Student Support Levels": "🎯 مستويات دعم الطالب",
        "👥 Support Groups": "👥 مجموعات الدعم",
        "📊 Download Excel": "📊 تحميل إكسل",

        # Comparison
        "📊 Comparison Table (Percentage Based)":
            "📊 جدول المقارنة (حسب النسبة المئوية)",
        "📢 Summary": "📢 الملخص",
        "Bar Chart": "رسم بياني شريطي",
        "Pie Chart": "رسم بياني دائري",
        "📈 Average Score Trend (%)":
            "📈 اتجاه متوسط الدرجات (%)",
        "📈 Student Growth (Difference)":
            "📈 نمو الطالب (الفرق)",
        "📈 Student Gap (Difference)":
            "📈 فجوة الطالب (الفرق)",

        # MAP
        "👥 Students": "👥 الطلاب",
        "📉 Previous Avg RIT": "📉 متوسط ريت السابق",
        "📈 Current Avg RIT": "📈 متوسط ريت الحالي",
        "🚀 Average Growth": "🚀 متوسط النمو",
        "🎯 Average Percentile": "🎯 متوسط النسبة المئوية",
        "📈 Student Growth": "📈 نمو الطالب",
        "📊 Growth Distribution": "📊 توزيع النمو",
        "📋 Student MAP Analysis": "📋 تحليل الطالب في ماب",
        "📥 Download MAP Analysis": "📥 تحميل تحليل ماب",
        "📄 Upload MAP Data Excel": "📄 تحميل إكسل بيانات ماب",
        "📋 MAP Data Preview": "📋 معاينة بيانات ماب",
        "📊 MAP Summary": "📊 ملخص ماب",
        "🎯 Student Percentile": "🎯 النسبة المئوية للطالب",
        "Growth Distribution": "توزيع النمو",

        # Achievement & Gaps
        "🎯 Achievement & Gaps (Internal vs MAP)":
            "🎯 الإنجاز والفجوات (التقييم الداخلي مقابل ماب)",
        "📄 Upload Single Sheet": "📄 تحميل ورقة واحدة",

        # Reports
        "Select Service": "اختر الخدمة",
        "Compare between sections": "مقارنة بين الأقسام",
        "🔍 Compare Between Sections": "🔍 مقارنة بين الأقسام",
        "Comparison Type": "نوع المقارنة",
        "By Assessment Objectives": "حسب أهداف التقييم",
        "By Assessment Total Mark": "حسب الدرجة الإجمالية",
        "By External Benchmark Assessment":
            "حسب تقييم المعيار الخارجي",
        "📚 By Assessment Objectives":
            "📚 حسب أهداف التقييم",
        "Number of classes": "عدد الفصول",
        "📄 Class": "📄 الصف",
        "file": "ملف",
        "📊 Band Distribution per Class":
            "📊 توزيع المستويات لكل صف",
        "✅ Comparison complete.": "✅ اكتملت المقارنة.",
        "📊 By Assessment Total Mark":
            "📊 حسب الدرجة الإجمالية",
        "🏢 By External Benchmark Assessment":
            "🏢 حسب تقييم المعيار الخارجي",

        # Misc
        "Max": "الحد الأقصى",
        "Below Acceptable": "أقل من المقبول",
        "Status": "الحالة",
        "Count": "العدد",
        "Band": "المستوى",
        "Assessment": "التقييم"
    }
}


# =========================================================
# TRANSLATION FUNCTION
# =========================================================

def t(text):
    return TRANSLATIONS.get(
        st.session_state.lang, {}
    ).get(text, text)


# =========================================================
# LANGUAGE SWITCH - TOP OF PAGE
# =========================================================

# RTL / LTR
if st.session_state.lang == "Arabic":
    direction = "rtl"
    text_align = "right"
else:
    direction = "ltr"
    text_align = "left"

st.markdown(
    f"""
    <style>

    .language-container {{
        direction: ltr;
        text-align: center;
        margin-bottom: 10px;
    }}

    .language-title {{
        font-size: 0.95rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 5px;
    }}

    .main-content {{
        direction: {direction};
        text-align: {text_align};
    }}

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton {{
        width: 100%;
    }}

    [data-testid="stSidebar"] .stButton button {{
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        background-color: transparent;
        width: 100%;
        text-align: left;
        padding: 0.5rem 0.75rem;
        font-size: 1rem;
    }}

    [data-testid="stSidebar"] .stButton button:hover {{
        background-color: rgba(128, 128, 128, 0.2);
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP LANGUAGE BUTTONS
# =========================================================

st.markdown(
    '<div class="language-container">'
    '<div class="language-title">🌐 Language / اللغة</div>'
    '</div>',
    unsafe_allow_html=True
)

lang_c1, lang_c2, lang_c3 = st.columns([2, 1, 1])

with lang_c2:
    if st.button(
        "🇬🇧 English",
        use_container_width=True,
        key="top_lang_en"
    ):
        st.session_state.lang = "English"
        st.rerun()

with lang_c3:
    if st.button(
        "🇱🇧 العربية",
        use_container_width=True,
        key="top_lang_ar"
    ):
        st.session_state.lang = "Arabic"
        st.rerun()

st.markdown("---")


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
            key=f"nav_{p}",
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


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def color_cell(v):

    if v == t("Growth"):
        return "background-color: green; color: white"

    if v == t("Decay"):
        return "background-color: red; color: white"

    if v == t("Same"):
        return "background-color: yellow"

    return ""


def support_level(pct):

    if pct is None:
        return t("N/A")

    try:
        p = float(pct)
    except:
        return t("N/A")

    if pd.isna(p):
        return t("N/A")

    if p < 25:
        return t("Intervention")

    elif p < 50:
        return t("Monitor")

    elif p < 75:
        return t("On Track")

    else:
        return t("Enrichment")


# =========================================================
# OBJECTIVES TEMPLATE
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


# =========================================================
# TOTAL TEMPLATE
# =========================================================

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


# =========================================================
# GAPS TEMPLATE
# =========================================================

def gaps_template():

    data = [
        [
            "Teacher Name: Example Teacher",
            "Class: Grade 7A",
            "Date: 27/08/2026",
            "Assessment name: Internal vs MAP",
            "Subject: Mathematics"
        ],
        [
            "Student Name",
            "Total of Internal",
            "Percentile of MAP"
        ],
        [
            "Over",
            100,
            ""
        ],
        [
            "Student 1",
            82,
            75
        ],
        [
            "Student 2",
            91,
            88
        ],
        [
            "Student 3",
            65,
            50
        ]
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


# =========================================================
# MAP TEMPLATE
# =========================================================

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

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:
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

def read_objectives_file(f):

    meta_raw = pd.read_excel(
        f,
        nrows=1,
        header=None
    )

    f.seek(0)

    meta = {}

    for c in meta_raw.columns:

        val = str(
            meta_raw.iloc[0, c]
        ).strip()

        if ":" in val:

            k, v = val.split(
                ":",
                1
            )

            meta[k.strip()] = v.strip()

    df = pd.read_excel(
        f,
        header=1
    )

    if str(
        df.iloc[0, 0]
    ).strip().lower() != "points for objectives":

        df = df.iloc[1:].reset_index(
            drop=True
        )

    mask = df.iloc[:, 0].astype(
        str
    ).str.contains(
        "Points for Objectives",
        case=False,
        na=False
    )

    if not mask.any():
        return None, None

    max_row = df[mask].iloc[0]

    raw_obj_cols = [
        c for c in df.columns
        if c != "Student Name"
    ]

    valid_cols = []
    total_max = 0.0

    for c in raw_obj_cols:

        hdr = str(c).strip()

        mx_raw = max_row[c]
        mx_str = str(mx_raw).strip()

        if (
            hdr != ""
            and hdr.lower() != "nan"
            and not hdr.startswith("Unnamed")
            and mx_str != ""
            and mx_str.lower() != "nan"
        ):

            try:
                mx = float(mx_raw)
            except:
                mx = 0.0

            if mx > 0:

                valid_cols.append(c)
                total_max += mx

    obj_cols = valid_cols

    df = df[
        ~mask
    ].copy()

    df = df.dropna(
        subset=[df.columns[0]]
    )

    df = df.rename(
        columns={
            df.columns[0]: "Student Name"
        }
    )

    if obj_cols:

        df = df[
            ["Student Name"] + obj_cols
        ]

    for c in obj_cols:

        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        ).fillna(0)

    if obj_cols:

        df["Obtained"] = df[
            obj_cols
        ].sum(axis=1)

    else:

        df["Obtained"] = 0

    if total_max:

        df["Pct"] = (
            df["Obtained"]
            / total_max
            * 100
        ).round(1)

    else:

        df["Pct"] = 0.0

    return meta, df


# =========================================================
# READ TOTAL FILE
# =========================================================

def read_total_file(f):

    raw = pd.read_excel(
        f,
        header=None
    )

    meta = {}

    for c in raw.iloc[0, :]:

        val = str(c).strip()

        if ":" in val:

            k, v = val.split(
                ":",
                1
            )

            meta[k.strip()] = v.strip()

    headers = [
        str(x).strip()
        for x in raw.iloc[1, :].tolist()
    ]

    total_idx = None

    for i in range(
        2,
        len(raw)
    ):

        if "total" in str(
            raw.iloc[i, 0]
        ).lower():

            total_idx = i
            break

    if total_idx is None:
        return None, None

    try:
        max_total = float(
            raw.iloc[
                total_idx,
                1
            ]
        )

    except:

        max_total = 100.0

    data = raw.iloc[
        2:,
        :
    ].copy()

    data.columns = headers

    data = data[
        data.iloc[:, 0]
        .astype(str)
        .str.lower()
        .str.contains("total")
        == False
    ]

    data = data.rename(
        columns={
            data.columns[0]:
            "Student Name"
        }
    )

    total_col = [
        c for c in data.columns
        if "total" in str(c).lower()
    ]

    if not total_col:
        return None, None

    total_col = total_col[0]

    data[total_col] = pd.to_numeric(
        data[total_col],
        errors="coerce"
    ).fillna(0)

    if max_total:

        data["Pct"] = (
            data[total_col]
            / max_total
            * 100
        ).round(1)

    else:

        data["Pct"] = 0.0

    return meta, data


# =========================================================
# READ GAPS FILE
# =========================================================

def read_gaps_file(f):

    raw = pd.read_excel(
        f,
        header=None
    )

    meta = {}

    for c in raw.iloc[0, :]:

        val = str(c).strip()

        if ":" in val:

            k, v = val.split(
                ":",
                1
            )

            meta[k.strip()] = v.strip()

    headers = [
        str(x).strip()
        for x in raw.iloc[1, :].tolist()
    ]

    total_idx = None

    for i in range(
        2,
        len(raw)
    ):

        if "over" in str(
            raw.iloc[i, 0]
        ).lower():

            total_idx = i
            break

    if total_idx is None:
        return None, None

    try:

        max_total = float(
            raw.iloc[
                total_idx,
                1
            ]
        )

    except:

        max_total = 100.0

    data = raw.iloc[
        2:,
        :
    ].copy()

    data.columns = headers

    data = data[
        data.iloc[:, 0]
        .astype(str)
        .str.lower()
        .str.contains("total")
        == False
    ]

    data = data.rename(
        columns={
            data.columns[0]:
            "Student Name"
        }
    )

    internal_col = [
        c for c in data.columns
        if "total of internal"
        in str(c).lower()
    ]

    map_col = [
        c for c in data.columns
        if "percentile of map"
        in str(c).lower()
    ]

    if not internal_col or not map_col:
        return None, None

    internal_col = internal_col[0]
    map_col = map_col[0]

    data[internal_col] = pd.to_numeric(
        data[internal_col],
        errors="coerce"
    ).fillna(0)

    data[map_col] = pd.to_numeric(
        data[map_col],
        errors="coerce"
    ).fillna(0)

    if max_total:

        data["Pct1"] = (
            data[internal_col]
            / max_total
            * 100
        ).round(1)

    else:

        data["Pct1"] = 0.0

    data["Pct2"] = data[
        map_col
    ].round(1)

    data = data[
        [
            "Student Name",
            "Pct1",
            "Pct2"
        ]
    ]

    return meta, data


# =========================================================
# READ SECTION FILE
# =========================================================

def read_section_file(f):

    meta, df = read_objectives_file(f)

    if meta is None:
        return (
            None,
            None,
            None,
            None,
            None
        )

    f.seek(0)

    raw_full = pd.read_excel(
        f,
        header=1
    )

    if str(
        raw_full.iloc[0, 0]
    ).strip().lower() != "points for objectives":

        desc_row = raw_full.iloc[0]
        max_row = raw_full.iloc[1]

    else:

        desc_row = None
        max_row = raw_full.iloc[0]

    obj_names = [
        c for c in df.columns
        if c not in [
            "Student Name",
            "Obtained",
            "Pct"
        ]
    ]

    obj_max = {}
    obj_desc = {}

    for c in obj_names:

        try:

            mx = float(
                max_row[c]
            )

        except:

            mx = 0

        obj_max[c] = mx

        if desc_row is not None:

            d = str(
                desc_row[c]
            ).strip()

            if (
                d == ""
                or d.lower() == "nan"
            ):

                d = str(c)

        else:

            d = str(c)

        obj_desc[c] = d

    return (
        meta,
        df,
        obj_names,
        obj_max,
        obj_desc
    )


# =========================================================
# MAIN CONTENT
# =========================================================

st.markdown(
    '<div class="main-content">',
    unsafe_allow_html=True
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

    st.title(
        t("Assessment Analysis")
    )

    st.markdown(
        t(
            "### Student Assessment & Achievement Dashboard"
        )
    )

    st.markdown(
        t(
            "Analyze MAP, internal assessments, grades, and student performance in seconds."
        )
    )

    st.markdown("---")

    st.markdown(
        t("### 📌 How to use")
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            t("### ① Upload Data")
            + "\n"
            + t(
                "Upload your Excel files with student marks."
            )
        )

    with c2:

        st.markdown(
            t("### ② Choose Analysis")
            + "\n"
            + t(
                "Pick the analysis type from the sidebar."
            )
        )

    with c3:

        st.markdown(
            t("### ③ View Insights")
            + "\n"
            + t(
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
        t(
            "📊 Assessment Analysis Overview"
        )
    )

    st.markdown(
        t(
            "The Assessment Analysis tool is designed to help teachers, coordinators, and school leaders analyze student achievement quickly and consistently."
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
            t(
                "📈 Class Total Average Analysis"
            )
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
        t(
            "Step 1: Upload Student Marks Excel"
        )
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

            if ":" in val:

                k, v = val.split(
                    ":",
                    1
                )

                meta_info[k.strip()] = v.strip()

        st.subheader(
            t("📋 Info")
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.markdown(
            f"**{t('👩‍🏫 Teacher:')}** "
            f"{meta_info.get('Teacher Name', 'N/A')}"
        )

        m2.markdown(
            f"**{t('🏫 Class:')}** "
            f"{meta_info.get('Class', 'N/A')}"
        )

        m3.markdown(
            f"**{t('📅 Date:')}** "
            f"{meta_info.get('Date', 'N/A')}"
        )

        m4.markdown(
            f"**{t('📝 Assessment:')}** "
            f"{meta_info.get('Assessment name', 'N/A')}"
        )

        st.markdown(
            f"### 📝 {t('Name:')} "
            f"**{meta_info.get('Assessment name', 'N/A')}** "
            f"| 📚 {t('Subject:')} "
            f"**{meta_info.get('Subject', 'N/A')}**"
        )

        raw = pd.read_excel(
            up_file,
            header=1
        )

        if str(
            raw.iloc[0, 0]
        ).strip().lower() != "points for objectives":

            desc_row = raw.iloc[0]

            raw_students = raw.iloc[
                1:
            ].reset_index(
                drop=True
            )

        else:

            desc_row = None
            raw_students = raw.copy()

        obj_desc = {}

        for c in raw.columns:

            if c != "Student Name":

                if desc_row is not None:

                    d = str(
                        desc_row[c]
                    ).strip()

                    if (
                        d == ""
                        or d.lower() == "nan"
                    ):

                        d = str(c)

                else:

                    d = str(c)

                obj_desc[c] = d

        all_obj_names = [
            c for c in raw_students.columns
            if c != "Student Name"
        ]

        mask = raw_students.iloc[
            :,
            0
        ].astype(str).str.contains(
            "Points for Objectives",
            case=False,
            na=False
        )

        if not mask.any():

            st.error(
                "❌ Need 'Points for Objectives' row."
            )

            st.stop()

        max_row = raw_students[
            mask
        ].iloc[0]

        obj_names = []
        obj_max = []

        for c in all_obj_names:

            hdr = str(c).strip()

            mx_raw = max_row[c]
            mx_str = str(mx_raw).strip()

            if (
                hdr != ""
                and hdr.lower() != "nan"
                and not hdr.startswith("Unnamed")
                and mx_str != ""
                and mx_str.lower() != "nan"
            ):

                try:

                    mx = float(mx_raw)

                except:

                    mx = 0.0

                if mx > 0:

                    obj_names.append(c)
                    obj_max.append(mx)

        student_df = raw_students[
            ~mask
        ].copy()

        student_df = student_df.dropna(
            subset=["Student Name"]
        )

        student_df = student_df[
            ["Student Name"] + obj_names
        ].copy()

        def is_absent(row):

            has_A = False
            all_empty = True

            for c in obj_names:

                v = row[c]

                if (
                    isinstance(v, str)
                    and "a" in v.lower()
                ):

                    has_A = True

                elif not (
                    pd.isna(v)
                    or (
                        isinstance(v, str)
                        and v.strip() == ""
                    )
                ):

                    all_empty = False

            return has_A or all_empty

        student_df["Absent"] = student_df.apply(
            is_absent,
            axis=1
        )

        for c in obj_names:

            student_df[c] = pd.to_numeric(
                student_df[c],
                errors="coerce"
            ).fillna(0)

        total_max = sum(obj_max)

        st.info(
            f"📋 {t('Auto Total Max Mark')} = "
            f"**{total_max}**"
        )

        st.markdown(
            f"### 📚 {t('Objectives')}"
        )

        for i, obj in enumerate(
            obj_names,
            1
        ):

            st.markdown(
                f"{i}. **{obj}** – "
                f"{obj_desc.get(obj, obj)}"
            )

        errors = []

        for _, row in student_df.iterrows():

            if row["Absent"]:
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
                        f"{c} Negative"
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
                "🚫 "
                + t("Fix data entry")
                + ":\n"
                + "\n".join(errors)
            )

        else:

            if st.button(
                t("Analyze Assessment"),
                key="analyze_assessment"
            ):

                res = []

                for _, row in student_df.iterrows():

                    if row["Absent"]:

                        res.append({
                            "Student Name":
                                row["Student Name"],
                            "Total": "-",
                            "Total %": None,
                            "Level":
                                t("Absent")
                        })

                        continue

                    ps = []
                    tot = 0

                    for j, c in enumerate(
                        obj_names
                    ):

                        mk = float(
                            row[c]
                        )

                        tot += mk

                        ps.append(
                            (
                                mk
                                / obj_max[j]
                            )
                            * 100
                            if obj_max[j]
                            else 0
                        )

                    tp = (
                        sum(ps)
                        / len(ps)
                        if ps
                        else 0
                    )

                    if tp < 60:
                        lvl = t("Fail")

                    elif tp < 70:
                        lvl = t("Acceptable")

                    elif tp < 80:
                        lvl = t("Good")

                    elif tp < 90:
                        lvl = t("Very Good")

                    else:
                        lvl = t("Outstanding")

                    res.append({
                        "Student Name":
                            row["Student Name"],
                        "Total":
                            tot,
                        "Total %":
                            round(tp, 1),
                        "Level":
                            lvl
                    })

                rdf = pd.DataFrame(res)

                rdf["Support Level"] = (
                    rdf["Total %"]
                    .apply(support_level)
                )

                st.header(
                    t(
                        "Step 2: Analysis Report"
                    )
                )

                c1, c2, c3, c4, c5, c6 = st.columns(6)

                cnt = (
                    rdf["Level"]
                    .value_counts()
                    .to_dict()
                )

                c1.metric(
                    t("Absent"),
                    cnt.get(
                        t("Absent"),
                        0
                    )
                )

                c2.metric(
                    t("Fail"),
                    cnt.get(
                        t("Fail"),
                        0
                    )
                )

                c3.metric(
                    t("Acceptable"),
                    cnt.get(
                        t("Acceptable"),
                        0
                    )
                )

                c4.metric(
                    t("Good"),
                    cnt.get(
                        t("Good"),
                        0
                    )
                )

                c5.metric(
                    t("Very Good"),
                    cnt.get(
                        t("Very Good"),
                        0
                    )
                )

                c6.metric(
                    t("Outstanding"),
                    cnt.get(
                        t("Outstanding"),
                        0
                    )
                )

                ts = len(rdf)

                valid_pct = rdf[
                    "Total %"
                ].dropna()

                if len(valid_pct):

                    ge60 = (
                        valid_pct >= 60
                    ).sum() / len(valid_pct) * 100

                    gt60 = (
                        valid_pct > 60
                    ).sum() / len(valid_pct) * 100

                    gt75 = (
                        valid_pct > 75
                    ).sum() / len(valid_pct) * 100

                else:

                    ge60 = 0
                    gt60 = 0
                    gt75 = 0

                if gt75 >= 90:
                    ov = t("Outstanding")

                elif gt60 >= 90:
                    ov = t("Very Good")

                elif gt60 >= 75:
                    ov = t("Good")

                elif ge60 >= 60:
                    ov = t("Acceptable")

                else:
                    ov = t("Below Acceptable")

                st.success(
                    f"**{ov}** "
                    f"({t('Max')} {total_max})"
                )

                cdf = (
                    rdf["Level"]
                    .value_counts()
                    .reset_index()
                )

                cdf.columns = [
                    "Level",
                    "Count"
                ]

                cdf["Level"] = pd.Categorical(
                    cdf["Level"],
                    categories=[
                        t(x)
                        for x in ORDER
                    ],
                    ordered=True
                )

                cdf = cdf.sort_values(
                    "Level"
                )

                v1, v2 = st.columns(2)

                with v1:

                    st.subheader(
                        t(
                            "📊 Student Achievement"
                        )
                    )

                    chart_df = rdf.dropna(
                        subset=["Total %"]
                    )

                    st.plotly_chart(
                        px.bar(
                            chart_df,
                            x="Student Name",
                            y="Total %",
                            color="Level",
                            range_y=[0, 100]
                        ),
                        use_container_width=True
                    )

                with v2:

                    st.subheader(
                        t(
                            "📊 Level Distribution"
                        )
                    )

                    st.plotly_chart(
                        px.pie(
                            cdf,
                            names="Level",
                            values="Count",
                            color="Level",
                            color_discrete_map={
                                t(k): v
                                for k, v
                                in COLORS.items()
                            },
                            hole=0.3
                        ),
                        use_container_width=True
                    )

                st.subheader(
                    t(
                        "🎯 Student Support Levels"
                    )
                )

                st.plotly_chart(
                    px.bar(
                        chart_df,
                        x="Student Name",
                        y="Total %",
                        color="Support Level",
                        range_y=[0, 100]
                    ),
                    use_container_width=True
                )

                support_count = (
                    rdf[
                        "Support Level"
                    ]
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

                eb = io.BytesIO()

                rdf.to_excel(
                    eb,
                    index=False
                )

                st.download_button(
                    t("📊 Download Excel"),
                    eb.getvalue(),
                    "Report.xlsx"
                )


# =========================================================
# CLASS TOTAL AVERAGE ANALYSIS
# =========================================================

elif page == "📈 Class Total Average Analysis":

    st.header(
        t(
            "📈 Class Total Average Analysis"
        )
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

    n_assess = st.number_input(
        t("🔢 Number of assessments"),
        min_value=2,
        max_value=10,
        value=2,
        step=1,
        key="nass"
    )

    files = []

    for i in range(
        int(n_assess)
    ):

        files.append(
            st.file_uploader(
                f"📄 {t('Assessment')} {i + 1}",
                type=["xlsx", "xls"],
                key=f"up{i}"
            )
        )

    if all(files):

        metas = []
        merged = None
        pct_cols = []
        names = []
        descriptions = []

        for i, f in enumerate(files):

            meta, df = read_objectives_file(f)

            if meta is None:

                st.error(
                    t(
                        "❌ File missing 'Points for Objectives' row."
                    )
                )

                st.stop()

            f.seek(0)

            raw_g = pd.read_excel(
                f,
                header=1
            )

            if str(
                raw_g.iloc[0, 0]
            ).strip().lower() != "points for objectives":

                desc_row_g = raw_g.iloc[0]

            else:

                desc_row_g = None

            obj_desc_g = {}

            for c in raw_g.columns:

                if c != "Student Name":

                    if desc_row_g is not None:

                        d = str(
                            desc_row_g[c]
                        ).strip()

                        if (
                            d == ""
                            or d.lower() == "nan"
                        ):

                            d = str(c)

                    else:

                        d = str(c)

                    obj_desc_g[c] = d

            metas.append(meta)

            names.append(
                meta.get(
                    "Assessment name",
                    "N/A"
                )
            )

            descriptions.append(
                obj_desc_g
            )

            col = f"Pct{i + 1}"

            keep = df[
                ["Student Name", "Pct"]
            ].rename(
                columns={
                    "Pct": col
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

            pct_cols.append(col)

        st.subheader(
            t("📋 Assessment Information")
        )

        for i, m in enumerate(metas):

            st.markdown(
                f"**File {i + 1} "
                f"({m.get('Assessment name', 'N/A')}):** "
                f"👩‍🏫 {m.get('Teacher Name', 'N/A')} | "
                f"🏫 {m.get('Class', 'N/A')} | "
                f"📅 {m.get('Date', 'N/A')} | "
                f"📚 {m.get('Subject', 'N/A')}"
            )

        merged[pct_cols] = (
            merged[pct_cols]
            .fillna(0)
        )

        merged["Difference"] = (
            merged[pct_cols[-1]]
            - merged[pct_cols[0]]
        ).round(1)

        merged["Status"] = (
            merged["Difference"]
            .apply(
                lambda d:
                t("Growth")
                if d > 0.5
                else t("Decay")
                if d < -0.5
                else t("Same")
            )
        )

        merged["Support Level"] = (
            merged[pct_cols[-1]]
            .apply(support_level)
        )

        st.subheader(
            t(
                "📊 Comparison Table (Percentage Based)"
            )
        )

        st.dataframe(
            merged.style.map(
                color_cell,
                subset=["Status"]
            ),
            use_container_width=True
        )

        cnt = (
            merged["Status"]
            .value_counts()
            .to_dict()
        )

        gc = cnt.get(
            t("Growth"),
            0
        )

        dc = cnt.get(
            t("Decay"),
            0
        )

        sc = cnt.get(
            t("Same"),
            0
        )

        st.subheader(
            t("📢 Summary")
        )

        m1, m2, m3 = st.columns(3)

        m1.metric(
            f"🟩 {t('Growth')}",
            gc
        )

        m2.metric(
            f"🟥 {t('Decay')}",
            dc
        )

        m3.metric(
            f"🟨 {t('Same')}",
            sc
        )

        cd = pd.DataFrame({
            "Status": [
                t("Growth"),
                t("Decay"),
                t("Same")
            ],
            "Count": [
                gc,
                dc,
                sc
            ]
        })

        cd["Status"] = pd.Categorical(
            cd["Status"],
            categories=[
                t("Decay"),
                t("Same"),
                t("Growth")
            ],
            ordered=True
        )

        v1, v2 = st.columns(2)

        with v1:

            st.markdown(
                f"**{t('Bar Chart')}**"
            )

            st.plotly_chart(
                px.bar(
                    cd,
                    x="Status",
                    y="Count",
                    color="Status",
                    color_discrete_map={
                        t("Growth"): "green",
                        t("Decay"): "red",
                        t("Same"): "yellow"
                    }
                ),
                use_container_width=True
            )

        with v2:

            st.markdown(
                f"**{t('Pie Chart')}**"
            )

            pf = px.pie(
                cd,
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

            pf.update_traces(
                textinfo="percent+label"
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
            "Assessment",
            "Average"
        ]

        avg["Assessment"] = (
            avg["Assessment"]
            .str.replace(
                "Pct",
                "Assess"
            )
        )

        st.subheader(
            t(
                "📈 Average Score Trend (%)"
            )
        )

        st.plotly_chart(
            px.line(
                avg,
                x="Assessment",
                y="Average",
                markers=True
            ),
            use_container_width=True
        )

        st.subheader(
            t(
                "📈 Student Growth (Difference)"
            )
        )

        st.plotly_chart(
            px.bar(
                merged,
                x="Student Name",
                y="Difference",
                color="Status"
            ),
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

        bufc = io.BytesIO()

        merged.to_excel(
            bufc,
            index=False
        )

        st.download_button(
            t("📊 Download Comparison Excel"),
            bufc.getvalue(),
            "Comparison.xlsx"
        )


# =========================================================
# MAP ANALYSIS
# =========================================================

elif page == "🗺️ MAP Analysis":

    st.title(
        t("🗺️ MAP Analysis")
    )

    st.info(
        t(
            "### What is a RIT Score?\n"
            "The RIT score is the scale used by MAP Growth to measure student achievement."
        )
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
                    t("❌ Missing columns: ")
                    + ", ".join(missing)
                )

                st.stop()

            map_df["Previous RIT"] = pd.to_numeric(
                map_df["Previous RIT"],
                errors="coerce"
            )

            map_df["Current RIT"] = pd.to_numeric(
                map_df["Current RIT"],
                errors="coerce"
            )

            map_df["Percentile"] = pd.to_numeric(
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
                    t("Growth")
                    if x > 0
                    else t("Decay")
                    if x < 0
                    else t("Same")
                )
            )

            map_df["Support Level"] = (
                map_df["Percentile"]
                .apply(
                    support_level
                )
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

            avg_previous = map_df[
                "Previous RIT"
            ].mean()

            avg_current = map_df[
                "Current RIT"
            ].mean()

            avg_growth = map_df[
                "RIT Growth"
            ].mean()

            avg_percentile = map_df[
                "Percentile"
            ].mean()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                t("👥 Students"),
                total_students
            )

            c2.metric(
                t("📉 Previous Avg RIT"),
                round(
                    avg_previous,
                    1
                )
            )

            c3.metric(
                t("📈 Current Avg RIT"),
                round(
                    avg_current,
                    1
                )
            )

            c4.metric(
                t("🚀 Average Growth"),
                round(
                    avg_growth,
                    1
                )
            )

            st.metric(
                t("🎯 Average Percentile"),
                round(
                    avg_percentile,
                    1
                )
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
                    t("📈 Student Growth")
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
                    t("📊 Growth Distribution")
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
                t("Growth Distribution")
            )

            st.subheader(
                t("🎯 Student Percentile")
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
                t("👥 Support Groups")
            )

            support_count = (
                map_df[
                    "Support Level"
                ]
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
                    subset=[
                        "Growth Status"
                    ]
                ),
                use_container_width=True
            )

            map_buffer = io.BytesIO()

            map_df.to_excel(
                map_buffer,
                index=False
            )

            st.download_button(
                t(
                    "📥 Download MAP Analysis"
                ),
                map_buffer.getvalue(),
                "MAP_Analysis_Report.xlsx"
            )

        except Exception as e:

            st.error(
                t(
                    "❌ Error reading MAP file: "
                )
                + str(e)
            )


# =========================================================
# ACHIEVEMENT & GAPS
# =========================================================

elif page == "🎯 Achievement & Gaps":

    st.header(
        t(
            "🎯 Achievement & Gaps (Internal vs MAP)"
        )
    )

    st.download_button(
        t("📥 Download Excel Template"),
        gaps_template(),
        "Achievement_Gaps_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    f = st.file_uploader(
        t("📄 Upload Single Sheet"),
        type=["xlsx", "xls"],
        key="gaps"
    )

    if f:

        m, df = read_gaps_file(f)

        if m is None:

            st.error(
                t(
                    "❌ File missing required rows/columns."
                )
            )

            st.stop()

        st.subheader(
            t("📋 Assessment Information")
        )

        df["Difference"] = (
            df["Pct2"]
            - df["Pct1"]
        ).round(1)

        df["Status"] = (
            df["Difference"]
            .apply(
                lambda d:
                t("Growth")
                if d > 0.5
                else t("Decay")
                if d < -0.5
                else t("Same")
            )
        )

        df["Support Level"] = (
            df["Pct2"]
            .apply(support_level)
        )

        st.subheader(
            t(
                "📊 Comparison Table (Percentage Based)"
            )
        )

        st.dataframe(
            df.style.map(
                color_cell,
                subset=["Status"]
            ),
            use_container_width=True
        )

        cnt = (
            df["Status"]
            .value_counts()
            .to_dict()
        )

        gc = cnt.get(
            t("Growth"),
            0
        )

        dc = cnt.get(
            t("Decay"),
            0
        )

        sc = cnt.get(
            t("Same"),
            0
        )

        st.subheader(
            t("📢 Summary")
        )

        mc1, mc2, mc3 = st.columns(3)

        mc1.metric(
            f"🟩 {t('Growth')}",
            gc
        )

        mc2.metric(
            f"🟥 {t('Decay')}",
            dc
        )

        mc3.metric(
            f"🟨 {t('Same')}",
            sc
        )

        cd = pd.DataFrame({
            "Status": [
                t("Growth"),
                t("Decay"),
                t("Same")
            ],
            "Count": [
                gc,
                dc,
                sc
            ]
        })

        cd["Status"] = pd.Categorical(
            cd["Status"],
            categories=[
                t("Decay"),
                t("Same"),
                t("Growth")
            ],
            ordered=True
        )

        v1, v2 = st.columns(2)

        with v1:

            st.markdown(
                f"**{t('Bar Chart')}**"
            )

            st.plotly_chart(
                px.bar(
                    cd,
                    x="Status",
                    y="Count",
                    color="Status",
                    color_discrete_map={
                        t("Growth"): "green",
                        t("Decay"): "red",
                        t("Same"): "yellow"
                    }
                ),
                use_container_width=True
            )

        with v2:

            st.markdown(
                f"**{t('Pie Chart')}**"
            )

            pf = px.pie(
                cd,
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

            pf.update_traces(
                textinfo="percent+label"
            )

            st.plotly_chart(
                pf,
                use_container_width=True
            )

        st.subheader(
            t(
                "📈 Student Gap (Difference)"
            )
        )

        st.plotly_chart(
            px.bar(
                df,
                x="Student Name",
                y="Difference",
                color="Status"
            ),
            use_container_width=True
        )

        support_count = (
            df["Support Level"]
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

        bufc = io.BytesIO()

        df.to_excel(
            bufc,
            index=False
        )

        st.download_button(
            t(
                "📊 Download Comparison Excel"
            ),
            bufc.getvalue(),
            "Internal_MAP_Comparison.xlsx"
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
            t(
                "🔍 Compare Between Sections"
            )
        )

        comp_type = st.radio(
            t("Comparison Type"),
            [
                t("By Assessment Objectives"),
                t("By Assessment Total Mark"),
                t("By External Benchmark Assessment")
            ],
            key="comparison_type"
        )

        # =================================================
        # BY OBJECTIVES
        # =================================================

        if comp_type == t(
            "By Assessment Objectives"
        ):

            n_sec = st.number_input(
                t("Number of classes"),
                min_value=2,
                max_value=10,
                value=2,
                step=1,
                key="nsec"
            )

            sec_files = [
                st.file_uploader(
                    f"📄 {t('Class')} {i + 1} "
                    f"{t('file')}",
                    type=["xlsx", "xls"],
                    key=f"secfile_{i}"
                )
                for i in range(
                    int(n_sec)
                )
            ]

            if all(sec_files):

                sections_data = []

                for idx, f in enumerate(
                    sec_files,
                    1
                ):

                    (
                        meta,
                        df,
                        obj_names,
                        obj_max,
                        obj_desc
                    ) = read_section_file(f)

                    if meta is None:

                        st.error(
                            t(
                                "❌ Class file invalid"
                            )
                        )

                        st.stop()

                    class_name = meta.get(
                        "Class",
                        f"{t('Class')} {idx}"
                    )

                    st.markdown(
                        f"### 📋 {t('Class')} "
                        f"{idx} {t('Info')}"
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

                    df["Band"] = (
                        df["Pct"]
                        .apply(band)
                    )

                    obj_avg = {
                        c:
                        (
                            df[c]
                            / obj_max[c]
                            * 100
                        ).mean()
                        if obj_max[c] > 0
                        else 0
                        for c in obj_names
                    }

                    sections_data.append({
                        "name": class_name,
                        "df": df,
                        "bands":
                            df["Band"]
                            .value_counts(),
                        "obj_avg":
                            obj_avg,
                        "obj_names":
                            obj_names,
                        "obj_desc":
                            obj_desc
                    })

                band_order = [
                    t(x)
                    for x in [
                        "Below 60% (Weak)",
                        "60-75% (Acceptable)",
                        "76-85% (Very Good)",
                        "86-100% (Excellent)"
                    ]
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

                plot_df = (
                    band_df
                    .reset_index()
                    .melt(
                        id_vars="index",
                        value_vars=band_order
                    )
                )

                plot_df.columns = [
                    t("Class"),
                    t("Band"),
                    t("Count")
                ]

                st.subheader(
                    t(
                        "📊 Band Distribution per Class"
                    )
                )

                st.plotly_chart(
                    px.bar(
                        plot_df,
                        x=t("Band"),
                        y=t("Count"),
                        color=t("Class"),
                        barmode="group",
                        text=t("Count")
                    ),
                    use_container_width=True
                )

                st.success(
                    t(
                        "✅ Comparison complete."
                    )
                )

        # =================================================
        # OTHER REPORT TYPES
        # =================================================

        elif comp_type == t(
            "By Assessment Total Mark"
        ):

            st.info(
                t(
                    "📊 By Assessment Total Mark"
                )
                + " — "
                + "This section is ready for the total-mark comparison."
            )

        elif comp_type == t(
            "By External Benchmark Assessment"
        ):

            st.info(
                t(
                    "🏢 By External Benchmark Assessment"
                )
                + " — "
                + "This section is ready for the external benchmark comparison."
            )


# =========================================================
# CLOSE MAIN CONTENT
# =========================================================

st.markdown(
    "</div>",
    unsafe_allow_html=True
)
