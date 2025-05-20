from datetime import datetime

import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.title("Inventory Transfer Dashboard (Auto-Fix Dates)")


uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = f"uploaded_{timestamp}.xlsx"
    with open(save_path, "wb") as out:
        out.write(uploaded_file.getbuffer())
    st.success(f"File saved as: {save_path}")

if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

# Parse date columns
df["Submission Date Parsed"] = pd.to_datetime(df["Submission Date"], errors="coerce")
df["Today's Date Parsed"] = pd.to_datetime(df["Today's Date"], errors="coerce")

# Fill missing Submission Dates with Today's Date
missing_submission = df["Submission Date Parsed"].isna()
df.loc[missing_submission, "Submission Date Parsed"] = df.loc[missing_submission, "Today's Date Parsed"]

# Show fix stats
fixed_count = missing_submission.sum()
total_rows = len(df)
st.caption(f"Total records: {total_rows}")
st.caption(f"Dates auto-fixed from 'Today's Date': {fixed_count}")

# Standardize date fields
df["Submission Date"] = df["Submission Date Parsed"]
df["Month"] = df["Submission Date"].dt.to_period("M").astype(str)

# Extract ONT Type
def extract_ont_type(text):
    if isinstance(text, str):
        matches = re.findall(r'ONT\s+([0-9A-Za-z\s\(\)-]+)', text)
        return ', '.join(match.strip() for match in matches)
    return None

df["ONT Type"] = df["Inventory to Transfer."].apply(extract_ont_type)

# Filters
available_techs = sorted(df["Tech"].dropna().unique())
available_months = sorted(df["Month"].unique())

selected_techs = st.multiselect("Filter by Tech", available_techs)
selected_months = st.multiselect("Filter by Month", available_months)

filtered_df = df.copy()
if selected_techs:
    filtered_df = filtered_df[filtered_df["Tech"].isin(selected_techs)]
if selected_months:
    filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]

# Show results
st.subheader("Filtered Results")
st.dataframe(filtered_df[["Submission Date", "Month", "Tech", "Transfer Inventory from:", "Type of transfer", "Inventory to Transfer.", "ONT Type"]])

# Technician Summary
st.subheader("Technician Summary")
if not filtered_df.empty:
    summary_df = (
        filtered_df.groupby("Tech")
        .agg(
            Installs=("ONT Type", "count"),
            First_Install=("Submission Date", "min"),
            Last_Install=("Submission Date", "max")
        )
        .sort_values(by="Installs", ascending=False)
        .reset_index()
    )
    st.dataframe(summary_df)

# Charts
st.subheader("ONT Type Usage by Tech")
if not filtered_df.empty:
    summary = filtered_df.groupby(["Tech", "ONT Type"]).size().unstack(fill_value=0)
    st.bar_chart(summary)

st.subheader("Installs Per Day")
installs_per_day = filtered_df.groupby(filtered_df["Submission Date"].dt.date).size()
if not installs_per_day.empty:
    import matplotlib.pyplot as plt
    fig_day, ax_day = plt.subplots()
    installs_per_day.plot(kind="bar", ax=ax_day)
    ax_day.set_title("Installs Per Day")
    ax_day.set_xlabel("Date")
    ax_day.set_ylabel("Number of Installs")
    ax_day.tick_params(axis='x', rotation=45)
    st.pyplot(fig_day)

st.subheader("Installs Per Month")
installs_per_month = filtered_df.groupby(filtered_df["Submission Date"].dt.to_period("M")).size()
if not installs_per_month.empty:
    fig_month, ax_month = plt.subplots()
    installs_per_month.plot(kind="bar", ax=ax_month)
    ax_month.set_title("Installs Per Month")
    ax_month.set_xlabel("Month")
    ax_month.set_ylabel("Number of Installs")
    ax_month.tick_params(axis='x', rotation=45)
    st.pyplot(fig_month)
