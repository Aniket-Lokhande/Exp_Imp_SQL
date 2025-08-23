import requests
import pandas as pd
import os
import re
import psycopg2
from groq import Groq
import streamlit as st


def get_csv_data():
    
    Desc_tb_path = 'Data/Description of Tables.csv'

    Desc_tb = pd.read_csv(Desc_tb_path)

    tables = "\n\nDatabase Schema Information : \n\n"

    for index, row in Desc_tb.iterrows():
        tables += f"{index+1}. Table: {row['Table']}\n"
        tables += f" - Description: {row['Description']}\n"
        tables += f" - Primary_key: {row['Primary_key']}\n"
        tables += f" - Schema: {row['Schema']}\n"
        tables += '\n\n'

    example_queries_path = 'Data/Example Queries.csv'

    example_queries_csv = pd.read_csv(example_queries_path)

    example_queries = "\n\nExample Queries: \n\n"

    for index,row in example_queries_csv.iterrows():
        example_queries += f"{index+1}. Query: {row['Query']}\n"
        example_queries += f" - SQL : {row['SQL']}\n"
        example_queries += '\n\n'

    folder_path = 'Data'

    table_columns = "\n\nBelow is the information for all tables\n\n"

    for filename in os.listdir(folder_path):
        if filename.startswith("Table") and filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)

            table_csv = pd.read_csv(file_path)

            table_columns += '\n\n' + filename + '\n\n'
            for index, row in table_csv.iterrows():
                table_columns += f"{index+1}. Column Name: {row['Name']}\n"
                table_columns += f" - Column DataType: {row['Type']}\n"
                table_columns += f" - Column Description: {row['Description']}\n"
                table_columns += f" - Column Example: {row['Example']}\n"
                table_columns += '\n\n'

    return tables, example_queries, table_columns

def get_prompt(query):
    tables, example_queries, table_columns = get_csv_data()

    prompt = f"""
    ### 🧠 Task

    You are a senior data analyst with full knowledge of the underlying database. Your job is to generate **syntactically correct and optimized PostgreSQL queries** to answer the user's question.
    strictly follow every instruction given in ### ⚙️ Must Follow Instructions section

    ---

    ### 📌 User Query:
    {query}

    ---

    ### 📚 Context

    #### 🗂️ Table Details:
    {tables}

    - Each row in the above section contains information about a table with:
        - **Name**: Table name
        - **Description**: What the table stores
        - **Primary_key**: Column(s) that form the primary key
        - **Schema**: Full name in format `schema.table`
    - **Always** use the full schema-qualified table name when referencing tables in the query.

    #### 📑 Column Details:
    {table_columns}

    - Each table section lists its columns:
        - **Name**: Column name
        - **Type**: Data type
        - **Description**: What the column stores
        - **Example**: Sample values

    #### 💡 Example Queries:
    {example_queries}

    - Each example contains:
        - **Query**: Natural language question
        - **SQL**: Corresponding SQL query
        - **Table and column used**: List of corresponding tables and there columns used in query
    - **Learn from these examples** — follow similar patterns in logic and structure.

    ---

    ### ⚙️ Must Follow Instructions (Strictly follow the following instructions)
       
        - Use cntry_trd_dft if the query is about countries.

        - Use cmd_trd_dft if the query is about commodities.
        
        - Do not use unnecessary columns in the sql query

        - Only reference the tables and schemas provided in the context.

        - Always use schema-qualified table names (e.g., schema.table).

        - Avoid unnecessary joins; include only the tables needed to answer the query.

        - Ensure all queries follow valid PostgreSQL syntax.

        - Always return the fields or values explicitly requested by the user.

        - Do not apply filters on aggregate functions in the WHERE clause — use the HAVING clause instead.

        - When using aggregate functions, always include a GROUP BY clause.

        - pct_change_yr_compr :

            1) If the query does not reference exp_pct_change, imp_pct_change, or trd_dft_pct_change → add filter: pct_change_yr_compr = 0

            2) If the query does reference one of reference exp_pct_change, imp_pct_change, or trd_dft_pct_change these columns:

                - If "previous year" is mentioned → use pct_change_yr_compr = 0.

                - If a specific year is mentioned → set pct_change_yr_compr to that year.

            3) Default (if unclear) → use pct_change_yr_compr = 0.

        - Year Filtering Rules :

            1) If no year is mentioned → use year = 202425.

            2) If the year is mentioned in financial formats (e.g., 2018/19, 2019/20, financial year 18-19) → convert to 201819, 201920, etc.

            3) If the year is mentioned as a single number (e.g., 2019, 2020, ......) → map it to the financial year format (201819, 201920, ......).
    ---

    ### 🧾 Output Template (Strictly Follow This):

    <SQL>
    SELECT ...
    FROM ...
    WHERE ...;
    </SQL>

    Replace the above with your final query inside the `<SQL>` and `</SQL>` tags. Nothing else should be printed.
"""


    return prompt
    
def get_sql(query):

    client = Groq(api_key="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")
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": get_prompt(query)
            }
        ]
    )

    response = completion.choices[0].message.content

    match = re.search(r"<SQL>(.*?)</SQL>", response, re.DOTALL)

    if match:
        sql_content = match.group(1)
        return sql_content 
    else:
        return ''
    

def get_dataframe(sql_content):
    
    conn = psycopg2.connect(
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        dbname="postgres",
        user="postgres.jkofgpvpovexxdpynwia",
        password="ShivShakti1/0",
        port=6543
    )

    # postgresql://postgres.jkofgpvpovexxdpynwia:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

    # Connect to your database
    print(sql_content)
    cur = conn.cursor()
    cur.execute(sql_content)
    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=columns)
    cur.close()
    conn.close()
    return df

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

