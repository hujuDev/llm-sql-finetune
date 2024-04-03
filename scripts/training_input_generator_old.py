import json
import os
import glob
import re
from tqdm import tqdm
import sqlite3

def load_sql_files(db_id, database_dir='../../database'):
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

def format_data(dataset_name='train_spider', database_dir='../database', data_dir='../data'):
    output_dir = os.path.join(data_dir, dataset_name)
    json_file = os.path.join('..', f'{dataset_name}.json')
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    print(f"The file contains {len(data)} entries.")
    
    training_data = []
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
        training_data.append(example_dict)

    os.makedirs(output_dir, exist_ok=True)
    batch_file_path = os.path.join(output_dir, f'{dataset_name}_data.json')
    with open(batch_file_path, 'w') as batch_file:
        json.dump(training_data, batch_file, indent=4)
    
    print(f"Data has been saved in {batch_file_path} with {len(training_data)} entries.")


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

def process_database_folders(root_folder):
    # Walk through all subdirectories of the root folder
    for subdir, dirs, files in os.walk(root_folder):
        # Check if a .sql file exists in the current directory
        if not glob.glob(os.path.join(subdir, '*.sql')):
            # If no .sql file exists, find the .sqlite file
            sqlite_files = glob.glob(os.path.join(subdir, '*.sqlite'))
            for sqlite_file in sqlite_files:
                # Define the path for the schema.sql file
                output_file = os.path.join(subdir, 'schema.sql')
                # Extract schema to the defined path
                extract_schema_to_sql(sqlite_file, output_file)


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Adjust the paths relative to the script's location
database_dir = os.path.join(script_dir, '..', 'database')
data_dir = os.path.join(script_dir, '..', 'data')

# Now call the functions with the adjusted paths
process_database_folders(database_dir)
format_data(dataset_name='dev', database_dir=database_dir, data_dir=data_dir)
format_data(dataset_name='train_spider', database_dir=database_dir, data_dir=data_dir)
format_data(dataset_name='train_others', database_dir=database_dir, data_dir=data_dir)
