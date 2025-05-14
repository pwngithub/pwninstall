
import streamlit as st
import pandas as pd

st.title("Submission Date Debugger")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if not uploaded_file:
    st.stop()

# Load file and parse submission date
df = pd.read_excel(uploaded_file)
df["Submission Date Parsed"] = pd.to_datetime(df["Submission Date"], errors="coerce")

# Mark rows with invalid Submission Dates
invalid_rows = df[df["Submission Date Parsed"].isna()]

st.write(f"Total rows in file: {len(df)}")
st.write(f"Rows with invalid Submission Date: {len(invalid_rows)}")

if not invalid_rows.empty:
    st.subheader("Rows with Invalid Submission Dates")
    st.dataframe(invalid_rows)
else:
    st.success("All rows have valid Submission Dates.")
