import re
import os
import psycopg2
from groq import Groq
import pandas as pd
from prompt import get_prompt
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
host = os.getenv("SUPABASE_HOST")
dbname=os.getenv("SUPABASE_DBNAME")
user=os.getenv("SUPABASE_USER")
password=os.getenv("SUPABASE_PASSWORD")
port=os.getenv("SUPABASE_PORT")


def get_sql(query: str) -> str:

    client = Groq(api_key=api_key)
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
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        port=port
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