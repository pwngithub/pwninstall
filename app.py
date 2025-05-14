
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.title("Inventory Transfer Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Extract ONT type
    def extract_ont_type(text):
        if isinstance(text, str):
            matches = re.findall(r'ONT\s+([0-9A-Za-z\s\(\)-]+)', text)
            return ', '.join(match.strip() for match in matches)
        return None

    df["ONT Type"] = df["Inventory to Transfer."].apply(extract_ont_type)

    techs = df["Tech"].dropna().unique()
    ont_types = df["ONT Type"].dropna().unique()
    submission_dates = df["Submission Date"].dropna().unique()

    selected_tech = st.multiselect("Filter by Tech", sorted(techs))
    selected_date = st.multiselect("Filter by Submission Date", sorted(submission_dates))
    selected_ont = st.multiselect("Filter by ONT Type", sorted(ont_types))

    filtered_df = df.copy()

    if selected_tech:
        filtered_df = filtered_df[filtered_df["Tech"].isin(selected_tech)]
    if selected_date:
        filtered_df = filtered_df[filtered_df["Submission Date"].isin(selected_date)]
    if selected_ont:
        filtered_df = filtered_df[filtered_df["ONT Type"].isin(selected_ont)]

    st.subheader("Filtered Results")
    st.dataframe(filtered_df[["Submission Date", "Tech", "Inventory to Transfer.", "ONT Type"]])

    st.subheader("ONT Type Usage by Tech")
    if not filtered_df.empty:
        summary = filtered_df.groupby(["Tech", "ONT Type"]).size().unstack(fill_value=0)
        st.bar_chart(summary)
