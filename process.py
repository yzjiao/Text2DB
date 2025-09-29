
import os
from util import *
import sqlite3
import nltk
import shutil
import json

def rename_db_to_sqlite(base_folder):
    # Walk through the directory
    for dirpath, dirnames, filenames in os.walk(base_folder):
        for filename in filenames:
            if filename.endswith('.db'):
                # Full path of the current file
                old_file = os.path.join(dirpath, filename)
                # New file name with '.sqlite' extension
                new_file = os.path.join(dirpath, filename[:-3] + '.sqlite')

                # Rename the file
                os.rename(old_file, new_file)
                print(f"Renamed {old_file} to {new_file}")



def process_folder(base_folder):
    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        
        # Process only directories
        if os.path.isdir(folder_path):
            new_folder_path = os.path.join(base_folder, "1" + folder)
            os.rename(folder_path, new_folder_path)

            # Iterate through the contents of the folder
            for root, dirs, files in os.walk(new_folder_path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    new_file_path = os.path.join(new_folder_path, name)
                    
                    # Rename specific files
                    if name == 'input.db':
                        new_file_path = os.path.join(new_folder_path, 'input.sqlite')
                    elif name == 'label.db':
                        new_file_path = os.path.join(new_folder_path, 'output.sqlite')
                    
                    # Move the file to the new folder
                    shutil.move(file_path, new_file_path)
                
                # Delete the inner folder if it's not the renamed top folder
                if root != new_folder_path:
                    os.rmdir(root)



def replace_newlines_in_db(db_path):
    import re
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table_name in tables:
        table_name = table_name[0]
        # Get the schema of the table
        cursor.execute(f"PRAGMA table_info(\"{table_name}\");")
        columns = cursor.fetchall()
        
        # Identify text-type columns (typically VARCHAR, CHAR, TEXT)
        text_columns = [col[1] for col in columns if 'TEXT' in col[2].upper() or 'CHAR' in col[2].upper()]
        
        # Update each text-type column, replacing '\n' with ' '
        for col in text_columns:
            if '\n' in col:
                print(db_path)
            new_col_name = col.replace('\n', '')
            new_col_name = re.sub(r'\s+', ' ', new_col_name)
            update_query = f"ALTER TABLE \"{table_name}\" RENAME COLUMN \"{col}\" TO \"{new_col_name}\""
            try:
                cursor.execute(update_query)
            except sqlite3.OperationalError as e:
                print(f"An error occurred: {e}")
                print(f"Failed query: {update_query}")
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()



def refine_column_values(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        # Get the list of columns in the table
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = cursor.fetchall()
        
        for column in columns:
            column_name = column[1]
            # Determine if any values in the column do not meet the specified conditions
            cursor.execute(f'''
                SELECT EXISTS(
                    SELECT 1
                    FROM "{table_name}"
                    WHERE "{column_name}" NOT LIKE '%.0'
                    AND "{column_name}" != ''
                    AND "{column_name}" IS NOT NULL
                );
            ''')
            does_not_meet_condition = cursor.fetchone()[0]
            # If no values that do not meet the conditions are found, proceed with update
            if not does_not_meet_condition:
                print(column_name)
                cursor.execute(f'''
                    UPDATE "{table_name}"
                    SET "{column_name}" = CASE
                        WHEN "{column_name}" LIKE '%.0' THEN SUBSTR("{column_name}", 1, LENGTH("{column_name}") - 2)
                        ELSE "{column_name}"
                    END
                    WHERE "{column_name}" LIKE '%.0';
                ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()





def rename_table(db_path, json_path):
    # Read the new table name from the JSON file
    with open(json_path, 'r') as file:
        data = json.load(file)
        new_table_name = data[0]['db_name'].replace(' ', '_')  # Adjust the key according to your JSON structure

    # Ensure that a new table name is provided
    if not new_table_name:
        print("New table name not found in JSON file.")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the current table name from the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    current_table_name = cursor.fetchone()

    # Ensure that there is exactly one table in the database
    if not current_table_name or len(current_table_name) != 1:
        print("Unexpected number of tables in the database.")
        return
    current_table_name = current_table_name[0]

    # Rename the table
    try:
        cursor.execute(f"ALTER TABLE \"{current_table_name}\" RENAME TO \"{new_table_name}\";")
        conn.commit()
        print(f"Table '{current_table_name}' successfully renamed to '{new_table_name}'.")
    except sqlite3.OperationalError as e:
        print(f"An error occurred while renaming the table: {e}")
    finally:
        conn.close()





hard, medium, easy = 0, 0, 0

from evaluate import compare_sqlite_dbs
import numpy as np

data_root = '/shared/data2/yizhuj2/text2db/dataset/'
filenames = load_filenames(data_root)
print(len(filenames))
print(len([f for f in filenames if 'di' in f]))
print(len([f for f in filenames if 'rp' in f]))
print(len([f for f in filenames if 'ca' in f]))
'''
for filename in filenames:
    path = os.path.join(data_root, filename, 'data.json')
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        input_db = os.path.join(data_root, filename, "input.sqlite")
        output_db = os.path.join(data_root, filename, "output.sqlite")
        tuples = compare_sqlite_dbs(input_db, output_db)
        print('num tuples', len(tuples))

        # table > 1 || #value > 20 || len. doc > 2000
        # table == 1 && (#value > 10 || len. doc > 1000)
        # table == 1 &&  #value <= 10 && len. doc < 1000

        text = data[0]['text'].split('\n\n\n\n\n\n\n')
        docs = [s.strip() for s in text if s.strip()]
        avg_words = []
        for doc in docs:
            # sentences = nltk.sent_tokenize(doc)
            # words_in_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
            # num_word = [len(words) for words in words_in_sentences]
            # avg_words.append(sum(num_word))
            num_word = len(nltk.word_tokenize(doc))
            avg_words.append(num_word)
        avg_len = np.mean(avg_words)

        print("avg_len", avg_len)
        
        if 'bird' in filename or len(tuples) > 20 or avg_len > 1000:
            data[0]['difficulty'] = 'hard'
            hard += 1
        elif len(tuples) > 5 or avg_len > 500:
            data[0]['difficulty'] = 'medium'
            medium += 1
        else:
            data[0]['difficulty'] = 'easy'
            easy += 1
        
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
print(hard, medium, easy)
'''