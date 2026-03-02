import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="قوَّم | Qawem", layout="wide")

# -------------------------
# Session Setup
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "reports" not in st.session_state:
    st.session_state.reports = []

# -------------------------
# Language & Theme
# -------------------------
col1, col2 = st.columns([8,2])
with col2:
    lang = st.selectbox("Language", ["العربية", "English"])
    mode = st.toggle("🌙 Dark Mode")

# -------------------------
# Welcome Page
# -------------------------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;color:#0B3C5D;'>قوَّم | Qawem</h1>", unsafe_allow_html=True)
    st.markdown("### National Data Quality Intelligence Platform")

    identifier = st.text_input("Email or Phone")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        st.session_state.logged_in = True
        st.rerun()

    st.markdown("Forgot Password? (Simulation)")
    st.markdown("Login via Nafath (Simulation)")

# -------------------------
# Main System
# -------------------------
else:

    menu = st.sidebar.radio("الخدمات", [
        "تحليل البيانات",
        "تقاريري",
        "المعلومات الشخصية",
        "الأسئلة الشائعة",
        "الدعم الفني"
    ])

    # -------------------------
    # Data Analysis
    # -------------------------
    if menu == "تحليل البيانات":

        st.header("رفع ملف CSV أو Excel")

        file = st.file_uploader("Upload File", type=["csv","xlsx"])

        if file:
            if file.name.endswith("csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            st.write("عدد السجلات:", len(df))
            st.write("عدد الأعمدة:", len(df.columns))

            # Missing %
            missing_percent = df.isnull().mean().mean()*100
            score = 100 - missing_percent

            # Outlier detection (numeric only)
            numeric_df = df.select_dtypes(include=np.number)
            outliers = ((numeric_df - numeric_df.mean()).abs() > 3*numeric_df.std()).sum().sum()

            # Duplicate detection
            duplicates = df.duplicated().sum()

            final_score = max(score - (outliers*2) - (duplicates*2),0)

            # Classification
            if final_score >= 95:
                level = "🟢 ممتاز"
            elif final_score >= 70:
                level = "🟡 جيد"
            else:
                level = "🔴 يحتاج مراجعة"

            st.metric("مؤشر الجودة العام", round(final_score,2))
            st.write("التصنيف:", level)
            st.write("عدد القيم الشاذة:", outliers)
            st.write("عدد التكرارات:", duplicates)

            st.bar_chart(df.isnull().sum())

            if st.button("تنظيف تلقائي"):
                df = df.drop_duplicates().fillna("N/A")
                st.success("تم إنشاء نسخة محسنة")
                st.download_button("تحميل النسخة النظيفة", df.to_csv(index=False), file_name="cleaned.csv")

            if st.button("حفظ في تقاريري"):
                st.session_state.reports.append({
                    "name": file.name,
                    "score": round(final_score,2)
                })
                st.success("تم حفظ التقرير")

    # -------------------------
    # Reports
    # -------------------------
    elif menu == "تقاريري":
        st.header("تقاريري السابقة")

        if len(st.session_state.reports) == 0:
            st.info("لا يوجد تقارير محفوظة")
        else:
            for r in st.session_state.reports:
                st.write(f"📄 {r['name']} - الجودة: {r['score']}")

    # -------------------------
    # Profile
    # -------------------------
    elif menu == "المعلومات الشخصية":
        st.header("بيانات المستخدم")

        name = st.text_input("الاسم", "ريمـاس")
        age = st.number_input("العمر", 18, 60, 22)
        national_id = st.text_input("رقم الهوية")
        org = st.text_input("الجهة")

        st.subheader("الأمان")new_pass = st.text_input("تغيير كلمة المرور", type="password")
        twofa = st.toggle("تفعيل التحقق بخطوتين (محاكاة)")

        if st.button("حفظ التغييرات"):
            st.success("تم تحديث البيانات")

        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.rerun()

    # -------------------------
    # FAQ
    # -------------------------
    elif menu == "الأسئلة الشائعة":
        st.header("الأسئلة الشائعة")

        st.write("ما هو قوَّم؟")
        st.write("منصة وطنية لقياس وتحسين جودة البيانات.")

        st.write("كيف يتم حساب الجودة؟")
        st.write("يتم تحليل النواقص، التكرارات، والقيم الشاذة.")

        st.write("هل يمكن تحميل نسخة نظيفة؟")
        st.write("نعم عبر زر التنظيف التلقائي.")

    # -------------------------
    # Support
    # -------------------------
    elif menu == "الدعم الفني":
        st.header("الدعم الفني")
        st.write("📞 920000000")
        st.write("✉️ Qawem@gov.sa")
