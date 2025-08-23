import pandas as pd
import os

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