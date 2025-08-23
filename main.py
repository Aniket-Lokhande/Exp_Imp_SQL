import streamlit as st
from utils import get_sql, get_dataframe

st.set_page_config(page_title="SQL Query Generator")

st.title("🧠 Natural Language to SQL")

query_input = st.text_area("Enter your question in natural language:")

if st.button("Generate SQL and Show Output"):

    sql = get_sql(query_input)

    st.subheader("🔍 Generated SQL")
    st.code(sql, language="sql")

    st.subheader("📊 Output DataFrame")
    df = get_dataframe(sql)
    st.write(df)
