import streamlit as st
import pandas as pd
import numpy as np
import difflib
from datetime import datetime
import io

st.set_page_config(page_title="قوَّم | Qawem", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "reports" not in st.session_state:
    st.session_state.reports = []
if "history" not in st.session_state:
    st.session_state.history = []
if "dark" not in st.session_state:
    st.session_state.dark = False
if "language" not in st.session_state:
    st.session_state.language = "AR"

# ---------------- LANGUAGE ----------------
lang = {
    "AR": {
        "title":"قوَّم | Qawem",
        "login":"تسجيل الدخول",
        "nafath":"الدخول عبر نفاذ الوطني",
        "analysis":"تحليل البيانات",
        "reports":"تقاريري",
        "profile":"الحساب والدعم",
        "timeline":"المقارنة الزمنية",
        "logout":"تسجيل خروج"
    },
    "EN":{
        "title":"Qawem",
        "login":"Login",
        "nafath":"Login via Nafath",
        "analysis":"Data Analysis",
        "reports":"My Reports",
        "profile":"Profile & Support",
        "timeline":"Time Comparison",
        "logout":"Logout"
    }
}

# ---------------- DARK MODE ----------------
if st.session_state.dark:
    st.markdown("""
    <style>
    body {background-color:#0B1E2D;color:white;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- TOP BAR ----------------
c1,c2,c3 = st.columns([6,2,2])

with c2:
    if st.selectbox("🌍",["العربية","English"])=="English":
        st.session_state.language="EN"
    else:
        st.session_state.language="AR"

with c3:
    st.session_state.dark = st.toggle("🌙", value=st.session_state.dark)

T = lang[st.session_state.language]

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center;color:#0B3C5D'>{T['title']}</h1>", unsafe_allow_html=True)

    st.text_input("Email or Phone")
    st.text_input("Password", type="password")

    if st.button(T["login"]):
        st.session_state.logged_in=True
        st.rerun()

    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.button("🔐 " + T["nafath"])
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SYSTEM ----------------
else:

    st.title(T["title"])

    col1,col2,col3,col4 = st.columns(4)

    if col1.button("📊 "+T["analysis"]): st.session_state.page="analysis"
    if col2.button("📁 "+T["reports"]): st.session_state.page="reports"
    if col3.button("📈 "+T["timeline"]): st.session_state.page="timeline"
    if col4.button("👤 "+T["profile"]): st.session_state.page="profile"

    if "page" not in st.session_state:
        st.session_state.page="analysis"

    # ---------- ANALYSIS ----------
    if st.session_state.page=="analysis":

        file = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx"])

        if file:
            df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

            st.subheader("📌 قبل التنظيف")
            st.dataframe(df.head())

            missing = df.isnull().sum().sum()
            duplicates = df.duplicated().sum()

            numeric = df.select_dtypes(include=np.number)
            z_scores = ((numeric - numeric.mean())/numeric.std()).abs()
            outliers = (z_scores>3).sum().sum()

            # Smart duplicate detection
            names = df.astype(str).apply(lambda x: x.str.lower())
            smart_dupes=0
            for i in range(len(names)):
                for j in range(i+1,len(names)):
                    ratio = difflib.SequenceMatcher(None," ".join(names.iloc[i])," ".join(names.iloc[j])).ratio()
                    if ratio>0.85:
                        smart_dupes+=1

            score_before = max(100-(missing*0.5)-(duplicates*2)-(outliers*2)-(smart_dupes*1.5),0)

            def classify(score):
                if score>=95: return "🟢 ممتاز"
                elif score>=70: return "🟡 جيد"
                else: return "🔴 يحتاج مراجعة"
            st.metric("Quality Before", round(score_before,2))
            st.write("التصنيف:", classify(score_before))

            # CLEAN
            cleaned = df.drop_duplicates().fillna("N/A")

            score_after = min(score_before+10,100)

            st.subheader("📌 بعد التنظيف")
            st.metric("Quality After", round(score_after,2))
            st.write("التصنيف:", classify(score_after))

            st.line_chart([score_before, score_after])

            st.subheader("تحليل الأخطاء")
            st.bar_chart({
                "Missing":[missing],
                "Duplicates":[duplicates],
                "Outliers":[outliers],
                "Smart Duplicates":[smart_dupes]
            })

            # Download Excel real
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                cleaned.to_excel(writer,index=False)
            st.download_button("تحميل Excel نظيف", buffer.getvalue(),"cleaned.xlsx")

            st.download_button("تحميل CSV نظيف", cleaned.to_csv(index=False),"cleaned.csv")

            if st.button("حفظ التقرير"):
                month = datetime.now().strftime("%Y-%m")
                st.session_state.history.append({"month":month,"score":score_after})
                st.session_state.reports.append({"name":file.name,"score":score_after})
                st.success("تم الحفظ")

    # ---------- REPORTS ----------
    if st.session_state.page=="reports":
        for r in st.session_state.reports:
            st.write(f"📄 {r['name']} - {r['score']}")

    # ---------- TIMELINE ----------
    if st.session_state.page=="timeline":
        st.subheader("📈 تطور جودة البيانات")
        if len(st.session_state.history)>0:
            df_hist=pd.DataFrame(st.session_state.history)
            st.line_chart(df_hist.set_index("month"))
        else:
            st.info("لا يوجد بيانات زمنية بعد")

    # ---------- PROFILE ----------
    if st.session_state.page=="profile":

        st.subheader("👤 البيانات الشخصية")
        st.text_input("الاسم","محمد")
        st.number_input("العمر",26,30,22)
        st.text_input("119990389")
        st.text_input("الهيئة العامة للإحصاء")

        st.subheader(" الخصوصية و الامان")
        st.text_input("تغيير كلمة المرور", type="password")
        st.toggle("تفعيل التحقق بخطوتين")

        st.subheader("❓ الأسئلة الشائعة")
        with st.expander("ما هو قوَّم؟"):
            st.write("نظام وطني لقياس وتحسين جودة البيانات.")
        with st.expander("كيف يعمل؟"):
            st.write("يقوم بتحليل القيم المفقودة والتكرار والقيم الشاذة.")
        with st.expander("ماهي الصيغة المدعومة؟"):
            st.write("يدعم النظام ملفات Excel , xls , xlsx ")
       

        st.subheader("📞 الدعم الفني")
        with st.expander("اتصل بنا"):
            st.write("920000000")
        with st.expander("راسلنا"):
            st.write("Qawem@gov.sa")

        if st.button(T["logout"]):
            st.session_state.logged_in=False
            st.rerun()
