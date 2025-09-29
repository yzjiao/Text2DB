import os
import re
import sys
import ast
import json
import time
import sqlite3
import requests
from tqdm import tqdm
from functools import wraps
from typing import get_type_hints

YOUR_API_KEY = os.environ.get("OPENAI_API_KEY")


def load_data(path):
    # Load JSON data from a file
    json_file = open(os.path.join(path, 'data.json') , "r")
    data = json.load(json_file)[0]
    # data['text'] = data['text'][:6000]
    data['docs'] = [s.strip() for s in data['text'].split('\n\n\n\n\n\n\n') if s.strip()]
    
    # Connect to the SQLite database
    database_path = os.path.join(path, 'input.sqlite') 
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query the sqlite_master table for schema
    cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE type='table';")
    schemas = cursor.fetchall()

    # Print out the schema
    db_schema = ''
    for entry in schemas:
        obj_type, obj_name, obj_sql = entry
        db_schema += f"Type: {obj_type} Name: {obj_name} SQL: {obj_sql}\n\n"
    data['db_schema'] = db_schema
    # print(data['db_schema'])
    # Query the data for all tables
    db_data = {}
    for entry in schemas:
        obj_type, obj_name, obj_sql = entry
        print(obj_name)
        cursor.execute(f'SELECT * FROM "{obj_name}"')
        column_names = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        # rows = rows[:10]
        list_of_dicts = [dict(zip(column_names, row)) for row in rows]
        # print(list_of_dicts[:5])
        db_data[obj_name] = list_of_dicts # [dict(row) for row in rows]
        # note that db_data is a list of tuple instead of dictionary.
    data['db_data'] = db_data

    conn.close()
    return data



def save_data(path, database, code_version=None):

    # Define the new database path
    os.makedirs(path, exist_ok=True)
    if code_version:
        new_code_path = os.path.join(path, 'codes.json')
        with open(new_code_path, 'w') as json_file:
            json.dump(code_version, json_file)

    new_database_path = os.path.join(path, 'output.sqlite')
    delete_if_file_exists(new_database_path)

    # Connect to the new SQLite database
    conn = sqlite3.connect(new_database_path)
    cursor = conn.cursor()

    for table_name, records in database.items():
        # Skip if no records for the table
        if not records or table_name == 'sqlite_sequence':
            continue
        
        # Enclose column names in double quotes to handle spaces and reserved words
        columns = ', '.join([f'"{col}"' for col in records[0].keys()])
        placeholders = ', '.join('?' * len(records[0]))

        # Construct and execute the CREATE TABLE statement
        create_stmt = f'CREATE TABLE "{table_name}" ({columns})'
        
        print(create_stmt)
        cursor.execute(create_stmt)

        # Construct and execute the INSERT INTO statement
        insert_stmt = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})'
        for record in records:
            cursor.execute(insert_stmt, list(record.values()))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    return


def load_filenames(directory):
    # List to hold file names
    filenames = []

    # os.listdir() returns a list of entries in the directory given by path
    for entry in os.listdir(directory):
        # Construct full file path
        full_path = os.path.join(directory, entry)
        # Check if it's a file and not a directory
        if os.path.isdir(full_path):
            filenames.append(entry)

    return filenames


def get_chat_response(messages, API_KEY=YOUR_API_KEY, model="gpt-4", temperature=1, max_tokens=None):
    ### gpt_version: gpt-3.5-turbo or gpt-4
    API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    while True: 
        try:
            response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                time.sleep(20)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            time.sleep(20)



def enforce_types(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get type hints of the function
        hints = get_type_hints(func)
        all_args = kwargs.copy()
        all_args.update(dict(zip(func.__code__.co_varnames, args)))
        for argument, argument_type in hints.items():
            if argument in all_args and not isinstance(all_args[argument], argument_type):
                raise TypeError(f"Argument {argument} of {func.__name__} is not of type {argument_type}")
        
        return func(*args, **kwargs)
    return wrapper



def delete_if_file_exists(file_path):
    # Check if the file exists
    if os.path.isfile(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file {file_path} has been deleted.")
    else:
        # File doesn't exist
        print(f"No action taken. The file {file_path} does not exist.")




def parse_schema_details(constructed_string):
    pattern = r"Type: (.+?) Name: (.+?) SQL: (.+?)"
    match = re.search(pattern, constructed_string)
    if match:
        obj_type = match.group(1)
        obj_name = match.group(2)
        obj_sql = match.group(3)
        return obj_type, obj_name, obj_sql
    else:
        return None, None, None