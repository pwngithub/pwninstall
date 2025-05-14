
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

    # Convert Submission Date to datetime
    df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")

    techs = df["Tech"].dropna().unique()
    vehicles = df["Transfer Inventory from:"].dropna().unique()
    job_types = df["Type of transfer"].dropna().unique()
    ont_types = df["ONT Type"].dropna().unique()
    submission_dates = df["Submission Date"].dropna().dt.date.unique()

    selected_tech = st.multiselect("Filter by Tech", sorted(techs))
    selected_vehicle = st.multiselect("Filter by Vehicle", sorted(vehicles))
    selected_job_type = st.multiselect("Filter by Job Type", sorted(job_types))
    selected_date = st.multiselect("Filter by Submission Date", sorted(submission_dates))
    selected_ont = st.multiselect("Filter by ONT Type", sorted(ont_types))

    filtered_df = df.copy()

    if selected_tech:
        filtered_df = filtered_df[filtered_df["Tech"].isin(selected_tech)]
    if selected_vehicle:
        filtered_df = filtered_df[filtered_df["Transfer Inventory from:"].isin(selected_vehicle)]
    if selected_job_type:
        filtered_df = filtered_df[filtered_df["Type of transfer"].isin(selected_job_type)]
    if selected_date:
        filtered_df = filtered_df[filtered_df["Submission Date"].dt.date.isin(selected_date)]
    if selected_ont:
        filtered_df = filtered_df[filtered_df["ONT Type"].isin(selected_ont)]

    st.subheader("Filtered Results")
    st.dataframe(filtered_df[["Submission Date", "Tech", "Transfer Inventory from:", "Type of transfer", "Inventory to Transfer.", "ONT Type"]])

    st.subheader("ONT Type Usage by Tech")
    if not filtered_df.empty:
        summary = filtered_df.groupby(["Tech", "ONT Type"]).size().unstack(fill_value=0)
        st.bar_chart(summary)

    st.subheader("ONT Installs Per Day")
    install_df = df[df["ONT Type"].notna()]
    installs_per_day = install_df.groupby(df["Submission Date"].dt.date).size()
    if not installs_per_day.empty:
        fig, ax = plt.subplots()
        installs_per_day.plot(kind="bar", ax=ax)
        ax.set_title("ONT Installs Per Day")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Installs")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
