import streamlit as st
import os
import pandas as pd

# App title
st.title("Data Explorer and Transformation Planner")

# --- Model File Display (kept from previous version) ---
st.sidebar.header("Model File")
model_file_path = "model.py"

if os.path.exists(model_file_path):
    st.sidebar.subheader(f"Content of `{model_file_path}`:")
    try:
        with open(model_file_path, "r") as f:
            file_content = f.read()
        st.sidebar.code(file_content, language="python")
    except Exception as e:
        st.sidebar.error(f"Error reading model file: {e}")
else:
    st.sidebar.warning(f"Model file not found: `{model_file_path}`")

# --- Orders Data Display ---
st.header("Orders Data")
orders_file_path = "data/orders_20250408_174258.xls"

if os.path.exists(orders_file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(orders_file_path, engine='openpyxl')
        st.subheader("Orders Data Preview:")
        st.dataframe(df)

        # Placeholder for transformation planning
        st.subheader("Transformation Plan:")
        st.text_area("Describe the transformations needed:", height=150, key="transformation_plan")

    except Exception as e:
        st.error(f"Error processing file '{orders_file_path}': {e}")
else:
    st.warning(f"Orders file not found: `{orders_file_path}`") 