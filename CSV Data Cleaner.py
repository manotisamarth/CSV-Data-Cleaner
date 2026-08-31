import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="CSV Data Cleaner",
    page_icon="🧹",
    layout="wide"
)

# Sidebar - Upload only
st.sidebar.title("🧹 Data Cleaner")
file = st.sidebar.file_uploader("Upload CSV", type="csv")

if file is None:
    st.title("🧹 CSV Data Cleaner")
    st.info("Upload a CSV file from the sidebar.")
    st.stop()

# Load
if "df" not in st.session_state or st.session_state.file != file.name:
    st.session_state.df = pd.read_csv(file)
    st.session_state.file = file.name

df = st.session_state.df

st.title("🧹 Universal CSV Data Cleaner")
st.caption(f"File: {file.name}")

# Overview
st.subheader("📊 Data Overview")

a, b, c, d = st.columns(4)
a.metric("Rows", len(df))
b.metric("Columns", len(df.columns))
c.metric("Missing Values", int(df.isna().sum().sum()))
d.metric("Duplicates", int(df.duplicated().sum()))

# Cleaning
st.divider()
st.subheader("🧹 Cleaning")

if st.button("Remove Duplicates"):
    old = len(df)
    df = df.drop_duplicates()
    st.session_state.df = df
    st.success(f"✅ {old - len(df)} duplicate rows removed.")

action = st.selectbox(
    "Missing Value Action",
    ["Do Nothing", "Drop Rows", "Fill Mean", "Fill Median", "Fill Mode"]
)

if st.button("Apply Missing Action"):

    missing = int(df.isna().sum().sum())

    if action == "Drop Rows":
        df = df.dropna()

    elif action == "Fill Mean":
        cols = df.select_dtypes("number").columns
        df[cols] = df[cols].fillna(df[cols].mean())

    elif action == "Fill Median":
        cols = df.select_dtypes("number").columns
        df[cols] = df[cols].fillna(df[cols].median())

    elif action == "Fill Mode":
        for col in df.columns:
            if df[col].isna().any():
                mode = df[col].mode()
                if not mode.empty:
                    df[col] = df[col].fillna(mode.iloc[0])

    st.session_state.df = df
    st.success(f"✅ {action} completed. {missing} missing values found.")

# Column management
st.divider()
st.subheader("📝 Column Management")

col1, col2 = st.columns(2)

with col1:
    remove_col = st.selectbox("Remove Column", df.columns)

    if st.button("🗑️ Remove Column"):
        df = df.drop(columns=remove_col)
        st.session_state.df = df
        st.success(f"✅ '{remove_col}' removed.")

with col2:
    rename_col = st.selectbox(
        "Rename Column",
        df.columns,
        key="rename"
    )

    new_name = st.text_input("New Name")

    if st.button("✏️ Rename Column"):
        if not new_name.strip():
            st.warning("⚠️ Enter a new name.")
        elif new_name in df.columns:
            st.warning("⚠️ Name already exists.")
        else:
            df = df.rename(columns={rename_col: new_name})
            st.session_state.df = df
            st.success(f"✅ '{rename_col}' renamed to '{new_name}'.")

# Data type
st.divider()
st.subheader("🔤 Change Data Type")

col1, col2 = st.columns(2)

with col1:
    type_col = st.selectbox(
        "Column",
        df.columns,
        key="type"
    )

with col2:
    dtype = st.selectbox(
        "Type",
        ["String", "Integer", "Float"]
    )

if st.button("Change Type"):

    try:
        if dtype == "String":
            df[type_col] = df[type_col].astype(str)

        else:
            df[type_col] = pd.to_numeric(
                df[type_col],
                errors="coerce"
            )

            if dtype == "Integer":
                df[type_col] = df[type_col].astype("Int64")

        st.session_state.df = df
        st.success(f"✅ '{type_col}' converted to {dtype}.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# Edit
st.divider()
st.subheader("📋 Edit Data")

edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    num_rows="dynamic"
)

if not edited_df.equals(st.session_state.df):
    st.session_state.df = edited_df
    st.success("✅ Data changes saved.")

# Current data
st.subheader("📋 Current Data")

st.dataframe(
    st.session_state.df,
    use_container_width=True
)

# Download
st.download_button(
    "📥 Download Cleaned CSV",
    st.session_state.df.to_csv(index=False),
    "cleaned_data.csv",
    "text/csv"
)

# Reset
if st.button("🔄 Reset Data"):
    st.session_state.df = pd.read_csv(file)
    st.success("✅ Data reset to original CSV.")