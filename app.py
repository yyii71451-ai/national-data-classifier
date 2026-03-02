import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="قوَّم | Qawem", layout="wide")

# -------------------------
# SESSION STATE
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "reports" not in st.session_state:
    st.session_state.reports = []
if "language" not in st.session_state:
    st.session_state.language = "AR"
if "dark" not in st.session_state:
    st.session_state.dark = False

# -------------------------
# LANGUAGE DICTIONARY
# -------------------------
text = {
    "AR": {
        "welcome": "قوَّم | Qawem",
        "login": "تسجيل الدخول",
        "analysis": "تحليل البيانات",
        "reports": "تقاريري",
        "profile": "الحساب والدعم",
        "upload": "رفع ملف CSV أو Excel",
        "clean": "تنظيف تلقائي",
        "save": "حفظ في تقاريري",
        "logout": "تسجيل خروج"
    },
    "EN": {
        "welcome": "Qawem",
        "login": "Login",
        "analysis": "Data Analysis",
        "reports": "My Reports",
        "profile": "Profile & Support",
        "upload": "Upload CSV or Excel",
        "clean": "Auto Clean",
        "save": "Save to Reports",
        "logout": "Logout"
    }
}

# -------------------------
# THEME
# -------------------------
if st.session_state.dark:
    st.markdown("""
        <style>
        body {background-color:#0B1E2D;color:white;}
        </style>
    """, unsafe_allow_html=True)

# -------------------------
# TOP BAR
# -------------------------
col1,col2,col3 = st.columns([6,2,2])

with col2:
    lang_choice = st.selectbox("🌍",["العربية","English"])
    if lang_choice == "English":
        st.session_state.language = "EN"
    else:
        st.session_state.language = "AR"

with col3:
    if st.toggle("🌙"):
        st.session_state.dark = True
    else:
        st.session_state.dark = False

T = text[st.session_state.language]

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:

    st.markdown(f"<h1 style='text-align:center;color:#0B3C5D'>{T['welcome']}</h1>", unsafe_allow_html=True)

    identifier = st.text_input("Email or Phone")
    password = st.text_input("Password", type="password")

    if st.button(T["login"]):
        st.session_state.logged_in = True
        st.rerun()

# -------------------------
# MAIN SYSTEM
# -------------------------
else:

    st.title(T["welcome"])

    # App-style boxes
    col1,col2,col3 = st.columns(3)

    if col1.button("📊 " + T["analysis"]):
        st.session_state.page = "analysis"
    if col2.button("📁 " + T["reports"]):
        st.session_state.page = "reports"
    if col3.button("👤 " + T["profile"]):
        st.session_state.page = "profile"

    if "page" not in st.session_state:
        st.session_state.page = "analysis"

    # -------------------------
    # ANALYSIS PAGE
    # -------------------------
    if st.session_state.page == "analysis":

        st.header(T["analysis"])
        file = st.file_uploader(T["upload"], type=["csv","xlsx"])

        if file:

            if file.name.endswith("csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            st.subheader("📌 قبل التنظيف")
            st.dataframe(df.head())

            missing_before = df.isnull().sum().sum()
            duplicates_before = df.duplicated().sum()

            numeric = df.select_dtypes(include=np.number)
            outliers_before = ((numeric - numeric.mean()).abs() > 3*numeric.std()).sum().sum()

            score_before = max(100 - (missing_before*0.5) - (duplicates_before*2) - (outliers_before*2),0)

            st.metric("Quality Score (Before)", round(score_before,2))

            # CLEAN
            cleaned = df.drop_duplicates().fillna("N/A")

            missing_after = cleaned.isnull().sum().sum()
            duplicates_after = cleaned.duplicated().sum()
            numeric2 = cleaned.select_dtypes(include=np.number)
            outliers_after = ((numeric2 - numeric2.mean()).abs() > 3*numeric2.std()).sum().sum()

            score_after = max(100 - (missing_after*0.5) - (duplicates_after*2) - (outliers_after*2),0)

            st.subheader("📌 بعد التنظيف")
            st.metric("Quality Score (After)", round(score_after,2))

            st.line_chart([score_before, score_after])

            st.bar_chart({
                "Before":[missing_before,duplicates_before,outliers_before],
                "After":[missing_after,duplicates_after,outliers_after]
            })

            st.download_button("تحميل CSV نظيف", cleaned.to_csv(index=False), "cleaned.csv")

            excel_data = cleaned.to_excel("cleaned.xlsx", index=False)
            st.download_button("تحميل Excel نظيف", cleaned.to_csv(index=False), "cleaned.xlsx")

            if st.button(T["save"]):
                st.session_state.reports.append({
                    "name": file.name,
                    "before": round(score_before,2),
                    "after": round(score_after,2),
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("Saved")

    # -------------------------
    # REPORTS PAGE
    # -------------------------
    if st.session_state.page == "reports":

        st.header(T["reports"])

        if len(st.session_state.reports)==0:
            st.info("No reports yet")
        else:
            for r in st.session_state.reports:
                st.markdown(f"""
                ### 📄 {r['name']}
                Before: {r['before']}
                After: {r['after']}
                Date: {r['date']}
                """)

    # -------------------------
    # PROFILE + SUPPORT PAGE
    # -------------------------
    if st.session_state.page == "profile":

        st.header("👤 الحساب")

        st.text_input("الاسم","ريماس")
        st.number_input("العمر",18,60,22)
        st.text_input("الهوية")
        st.text_input("الجهة")

        st.subheader("🔐 الأمان")
        st.text_input("تغيير كلمة المرور", type="password")
        st.toggle("تفعيل التحقق بخطوتين")

        st.subheader("📞 الدعم الفني")
        st.write("920000000")
        st.write("Qawem@gov.sa")

        st.subheader("❓ الأسئلة الشائعة")

        with st.expander("ما هو قوَّم؟"):
            st.write("منصة وطنية لرفع جودة البيانات المؤسسية.")

        with st.expander("كيف يتم حساب الجودة؟"):
            st.write("يتم تحليل القيم المفقودة والتكرار والقيم الشاذة.")

        with st.expander("كيف أحمل النسخة النظيفة؟"):
            st.write("بعد التحليل يظهر زر تحميل CSV و Excel.")

        if st.button(T["logout"]):
            st.session_state.logged_in=False
            st.rerun()
