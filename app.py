import streamlit as st
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import matplotlib.pyplot as plt

st.set_page_config(page_title="المصنف الوطني الذكي", layout="wide")

st.title("المصنف الوطني الذكي")
st.write("نظام ذكي لتحليل جودة البيانات")

uploaded_file = st.file_uploader("ارفع ملف CSV أو Excel", type=["csv","xlsx"])

def calculate_quality(row):
    score = 100
    missing = row.isnull().sum()
    score -= missing * 5
    return max(score,0)

if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df["Quality Score"] = df.apply(calculate_quality, axis=1)
    overall_score = df["Quality Score"].mean()

    st.metric("مؤشر الجودة العام", f"{overall_score:.2f}/100")

    st.dataframe(df)
