
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.title("Inventory Transfer Dashboard (Auto-Fix Dates)")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if not uploaded_file:
    st.stop()

# Load and attempt to parse both date columns
df = pd.read_excel(uploaded_file)

# Try parsing Submission Date
df["Submission Date Parsed"] = pd.to_datetime(df["Submission Date"], errors="coerce")
df["Today's Date Parsed"] = pd.to_datetime(df["Today's Date"], errors="coerce")

# Fix missing Submission Dates using Today's Date
missing_submission = df["Submission Date Parsed"].isna()
df.loc[missing_submission, "Submission Date Parsed"] = df.loc[missing_submission, "Today's Date Parsed"]

# Count how many were replaced
fixed_count = missing_submission.sum()
total_rows = len(df)

# Display info
st.caption(f"Total records: {total_rows}")
st.caption(f"Dates auto-fixed from 'Today's Date': {fixed_count}")

# Use the repaired submission date
df["Submission Date"] = df["Submission Date Parsed"]
df["Month"] = df["Submission Date"].dt.to_period("M").astype(str)

# Extract ONT type
def extract_ont_type(text):
    if isinstance(text, str):
        matches = re.findall(r'ONT\s+([0-9A-Za-z\s\(\)-]+)', text)
        return ', '.join(match.strip() for match in matches)
    return None

df["ONT Type"] = df["Inventory to Transfer."].apply(extract_ont_type)

# Filter by Tech
available_techs = sorted(df["Tech"].dropna().unique())
selected_techs = st.multiselect("Filter by Tech", available_techs)

filtered_df = df.copy()
if selected_techs:
    filtered_df = filtered_df[filtered_df["Tech"].isin(selected_techs)]

# Results
st.subheader("Filtered Results")
st.dataframe(filtered_df[["Submission Date", "Month", "Tech", "Transfer Inventory from:", "Type of transfer", "Inventory to Transfer.", "ONT Type"]])

# Charts
st.subheader("ONT Type Usage by Tech")
if not filtered_df.empty:
    summary = filtered_df.groupby(["Tech", "ONT Type"]).size().unstack(fill_value=0)
    st.bar_chart(summary)

st.subheader("Installs Per Day")
installs_per_day = filtered_df.groupby(filtered_df["Submission Date"].dt.date).size()
if not installs_per_day.empty:
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
