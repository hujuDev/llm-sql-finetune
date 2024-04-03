import json
import os
import glob
import re
from tqdm import tqdm
import sqlite3

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '../data')
database_dir = os.path.join(data_dir, 'datasets/spider/database')

def load_sql_files(db_id, database_dir):
    db_path = os.path.join(database_dir, db_id)
    sql_files = glob.glob(os.path.join(db_path, '*.sql'))
    if not sql_files:
        return None
    
    create_table_statements = "\nSchema:"
    create_table_regex = r'CREATE TABLE\s+.*?\(.*?\);'
    for sql_file in sql_files:
        with open(sql_file, 'r', encoding='utf-8') as file:
            file_content = file.read()
            matches = re.findall(create_table_regex, file_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                create_table_statements += "\n" + match
    return create_table_statements

def format_data(dataset_name, data_dir, database_dir):
    output_dir = os.path.join(data_dir, 'datasets_json')
    
    json_file = os.path.join(data_dir, 'datasets/spider', f'{dataset_name}.json')
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    print(f"The file contains {len(data)} entries.")
    
    json_data = []
    for entry in tqdm(data, desc=f"Processing dataset"):
        question = "Question: " + entry['question']
        db_id = entry['db_id']
        query = entry.get('query', '')
        schema_sql = load_sql_files(db_id, database_dir)
        if schema_sql is None:
            continue

        input_field = f"{question}{schema_sql}"
        example_dict = {
            "Question": question,
            "Schema": schema_sql,
            "Input": input_field,
            "query": query,
            "db_id": db_id
        }
        json_data.append(example_dict)

    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, f'spider_{dataset_name}.json')
    with open(output_file_path, 'w') as output_file:
        json.dump(json_data, output_file, indent=4)
    
    print(f"Data has been saved in {output_file_path} with {len(json_data)} entries.")


def extract_schema_to_sql(db_path, output_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch "CREATE TABLE" statements
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema = cursor.fetchall()

    # Write schema to the output file
    with open(output_file, 'w') as f:
        for table_schema in schema:
            f.write('%s;\n\n' % table_schema[0])

    # Close the connection
    conn.close()
    print(f"Schema extracted to {output_file}")

def add_missing_sql_files(database_dir):
    # Add Missing .sql files for databases
    for subdir, dirs, files in os.walk(database_dir):
        # Check if a .sql file exists in the current directory
        if not glob.glob(os.path.join(subdir, '*.sql')):
            # If no .sql file exists, find the .sqlite file
            sqlite_files = glob.glob(os.path.join(subdir, '*.sqlite'))
            for sqlite_file in sqlite_files:
                # Define the path for the schema.sql file
                output_file = os.path.join(subdir, 'schema.sql')
                # Extract schema to the defined path
                extract_schema_to_sql(sqlite_file, output_file)


add_missing_sql_files(database_dir)

format_data('dev', data_dir, database_dir)
format_data('train_spider', data_dir, database_dir)
format_data('train_others', data_dir, database_dir)
