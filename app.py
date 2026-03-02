import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.platypus import TableStyle

st.set_page_config(page_title="قَوَّم | Qawem", layout="wide")

# ======================
# 🎨 Royal Navy Theme
# ======================
st.markdown("""
<style>
.stApp {
    background-color:#0A1F33;
    color:white;
}
.main-title {
    font-size:42px;
    font-weight:800;
    color:#1F77B4;
}
.metric-box {
    background-color:#122B45;
    padding:15px;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# 🔐 Login System
# ======================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    st.markdown('<p class="main-title">قَوَّم | Qawem</p>', unsafe_allow_html=True)
    st.write("منصة وطنية لذكاء جودة البيانات")

    email = st.text_input("Email / Phone")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Login"):
        if email and password:
            st.session_state.auth = True
            st.session_state.user = email
            st.rerun()
        else:
            st.error("Enter credentials")

    if col2.button("Forgot Password"):
        st.info("OTP sent (simulation)")

    st.markdown("---")
    st.markdown("[Login via Nafath](https://iam.gov.sa)")

else:

    # ======================
    # Sidebar Navigation
    # ======================
    page = st.sidebar.radio("Menu", [
        "Dashboard",
        "My Reports",
        "Security",
        "Help Center",
        "Contact",
        "About"
    ])

    st.sidebar.write(f"👤 {st.session_state.user}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"auth": False}))

    # ======================
    # Dashboard
    # ======================
    if page == "Dashboard":

        st.markdown('<p class="main-title">Data Intelligence Dashboard</p>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx"])

        if uploaded:

            if uploaded.name.endswith("csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)

            # ===== Advanced Quality Score =====
            missing = df.isnull().sum().sum()
            duplicates = df.duplicated().sum()
            total_cells = df.shape[0] * df.shape[1]

            completeness = 100 - (missing / total_cells * 100)
            uniqueness = 100 - (duplicates / len(df) * 100)

            quality_score = (completeness * 0.6) + (uniqueness * 0.4)

            # KPIs
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall Quality Score", f"{quality_score:.1f}/100")
            c2.metric("Missing Values", missing)
            c3.metric("Duplicate Rows", duplicates)

            # Classification
            if quality_score >= 90:
                level = "Excellent"
            elif quality_score >= 70:
                level = "Good"
            else:
                level = "Needs Improvement"

            st.success(f"Classification: {level}")

            # Chart
            fig, ax = plt.subplots()
            ax.pie(
                [completeness, uniqueness],
                labels=["Completeness","Uniqueness"],
                autopct="%1.1f%%"
            )
            st.pyplot(fig)

            # Save report to session
            if "reports" not in st.session_state:
                st.session_state.reports = []

            report_data = {
                "name": uploaded.name,
                "score": quality_score,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            st.session_state.reports.append(report_data)

            # Download Excel
            output_excel = BytesIO()
            df.to_excel(output_excel, index=False)
            st.download_button(
                "Download Excel Report",
                output_excel.getvalue(),
                file_name="Qawem_Report.xlsx"
            )

            # Generate PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            elements = []

            data = [
                ["Qawem Data Quality Report"],
                [f"Score: {quality_score:.1f}/100"],
                [f"Classification: {level}"],
                [f"Date: {datetime.now()}"]
            ]

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('GRID',(0,0),(-1,-1),1,colors.black)
            ]))

            elements.append(table)
            doc.build(elements)

            st.download_button(
                "Download Official PDF",
                buffer.getvalue(),
                file_name="Qawem_Official_Report.pdf"
            )

    # ======================
    # My Reports
    # ======================
    elif page == "My Reports":
        st.title("My Reports History")
        if "reports" in st.session_state:
            for r in st.session_state.reports:
                st.write(f"📊 {r['name']} | {r['score']:.1f} | {r['date']}")
        else:
            st.info("No reports yet")

    elif page == "Security":
        st.title("Security Settings")
        st.text_input("Current Password", type="password")
        st.text_input("New Password", type="password")
        st.button("Update Password")

    elif page == "Help Center":
        st.title("FAQs")
        st.expander("What is Qawem?").write("AI-based national data quality platform.")
        st.expander("How scoring works?").write("Based on completeness and uniqueness metrics.")

    elif page == "Contact":
        st.title("Contact Us")
        st.write("📧 support@qawem.sa")
        st.write("📱 0500000000")

    elif page == "About":
        st.title("About Qawem")
        st.write("Qawem is a national AI-powered data quality governance platform.")
