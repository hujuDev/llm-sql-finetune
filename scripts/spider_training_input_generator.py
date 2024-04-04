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

def combine_json_files(file_path_1, file_path_2, output_file_path):
    # Read content from the first file
    with open(file_path_1, 'r', encoding='utf-8') as file:
        data_1 = json.load(file)
    
    # Read content from the second file
    with open(file_path_2, 'r', encoding='utf-8') as file:
        data_2 = json.load(file)
    
    # Combine the data from both files
    combined_data = data_1 + data_2
    
    # Write the combined data to a new file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(combined_data, file, indent=4)

def copy_sql_to_txt(source_file_path, destination_file_path):
    # Open the source SQL file and read its content
    with open(source_file_path, 'r', encoding='utf-8') as source_file:
        content = source_file.read()
    
    # Open the destination text file and write the content
    with open(destination_file_path, 'w', encoding='utf-8') as destination_file:
        destination_file.write(content)

    print(f"Content successfully copied from {source_file_path} to {destination_file_path}.")

add_missing_sql_files(database_dir)

format_data('dev', data_dir, database_dir)
format_data('train_spider', data_dir, database_dir)
format_data('train_others', data_dir, database_dir)

combine_json_files(os.path.join(data_dir, 'datasets_json/spider_train_spider.json'), os.path.join(data_dir, 'datasets_json/spider_train_others.json'), os.path.join(data_dir, 'datasets_json/spider_train_combined.json'))

copy_sql_to_txt(os.path.join(data_dir, 'datasets/spider/dev_gold.sql'), os.path.join(script_dir, '../evaluation/gold/dev_gold.txt'))
copy_sql_to_txt(os.path.join(data_dir, 'datasets/spider/train_gold.sql'), os.path.join(script_dir, '../evaluation/gold/train_gold.txt'))
