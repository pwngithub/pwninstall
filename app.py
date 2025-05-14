
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.title("Inventory Transfer Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if not uploaded_file:
    st.stop()

# Load file and parse Submission Date only
df = pd.read_excel(uploaded_file)
df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")
df["Month"] = df["Submission Date"].dt.to_period("M").astype(str)

# Debug preview of rows 25–35
st.write("Submission Date values from row 25–35:")
st.dataframe(df.loc[25:35, ["Submission Date"]])

# Extract ONT type
def extract_ont_type(text):
    if isinstance(text, str):
        matches = re.findall(r'ONT\s+([0-9A-Za-z\s\(\)-]+)', text)
        return ', '.join(match.strip() for match in matches)
    return None

df["ONT Type"] = df["Inventory to Transfer."].apply(extract_ont_type)

# Optional tech filter
available_techs = sorted(df["Tech"].dropna().unique())
selected_techs = st.multiselect("Filter by Tech", available_techs)

filtered_df = df.copy()
if selected_techs:
    filtered_df = df[df["Tech"].isin(selected_techs)]

# Display counts and data
st.caption(f"Total records in file: {len(df)}")
st.caption(f"Filtered records: {len(filtered_df)}")

st.subheader("Filtered Results")
if not filtered_df.empty:
    st.dataframe(filtered_df[["Submission Date", "Month", "Tech", "Transfer Inventory from:", "Type of transfer", "Inventory to Transfer.", "ONT Type"]])
else:
    st.warning("No records match the selected filters.")

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
