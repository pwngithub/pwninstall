
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
    df["Month"] = df["Submission Date"].dt.to_period("M").astype(str)

    # Recalculate month filter options based on uploaded file content
    available_months = sorted(df["Month"].dropna().unique())
    available_techs = sorted(df["Tech"].dropna().unique())

    selected_tech = st.multiselect("Filter by Tech", available_techs)
    selected_month = st.multiselect("Filter by Month", available_months)

    filtered_df = df.copy()
    if selected_tech:
        filtered_df = filtered_df[filtered_df["Tech"].isin(selected_tech)]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_month)]

    st.subheader("Filtered Results")
    st.dataframe(filtered_df[["Submission Date", "Tech", "Transfer Inventory from:", "Type of transfer", "Inventory to Transfer.", "ONT Type"]])

    st.subheader("ONT Type Usage by Tech")
    if not filtered_df.empty:
        summary = filtered_df.groupby(["Tech", "ONT Type"]).size().unstack(fill_value=0)
        st.bar_chart(summary)

    st.subheader("Installs Per Day")
    install_df = filtered_df[filtered_df["ONT Type"].notna()]
    installs_per_day = install_df.groupby(install_df["Submission Date"].dt.date).size()
    if not installs_per_day.empty:
        fig_day, ax_day = plt.subplots()
        installs_per_day.plot(kind="bar", ax=ax_day)
        ax_day.set_title("Installs Per Day")
        ax_day.set_xlabel("Date")
        ax_day.set_ylabel("Number of Installs")
        ax_day.tick_params(axis='x', rotation=45)
        st.pyplot(fig_day)

    st.subheader("Installs Per Month")
    installs_per_month = install_df.groupby(install_df["Submission Date"].dt.to_period("M")).size()
    if not installs_per_month.empty:
        fig_month, ax_month = plt.subplots()
        installs_per_month.plot(kind="bar", ax=ax_month)
        ax_month.set_title("Installs Per Month")
        ax_month.set_xlabel("Month")
        ax_month.set_ylabel("Number of Installs")
        ax_month.tick_params(axis='x', rotation=45)
        st.pyplot(fig_month)
