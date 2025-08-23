import re
import psycopg2
from groq import Groq
import pandas as pd
from prompt import get_prompt

def get_sql(query: str) -> str:

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