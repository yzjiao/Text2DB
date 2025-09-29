import sqlite3
import os
from util import load_filenames

NULL_WORDS = ['', 'none', 'None', 'NONE', 'null', None, 'N/A']

'''
def compare_sqlite_dbs(old_db_path, new_db_path):
    # Connect to the SQLite databases
    old_conn = sqlite3.connect(old_db_path)
    new_conn = sqlite3.connect(new_db_path)
    
    # Get a cursor for each database
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    # Get the list of all tables in both databases
    old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    old_tables = set([row[0] for row in old_cursor.fetchall()])
    new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    new_tables = set([row[0] for row in new_cursor.fetchall()])
    
    # Find tables that are in both databases
    common_tables = old_tables.intersection(new_tables)
    all_changes = []

    for table in common_tables:
        # Get column info for both old and new tables
        old_cursor.execute(f"PRAGMA table_info(\"{table}\")")
        old_columns = [info[1] for info in old_cursor.fetchall()]
        new_cursor.execute(f"PRAGMA table_info(\"{table}\")")
        new_columns = [info[1] for info in new_cursor.fetchall()]
        primary_key_column = old_columns[0] if old_columns else new_columns[0]

        # Fetch all rows from old and new tables
        old_cursor.execute(f"SELECT * FROM \"{table}\"")
        old_rows = {row[0]: row for row in old_cursor.fetchall()}
        new_cursor.execute(f"SELECT * FROM \"{table}\"")
        new_rows = {row[0]: row for row in new_cursor.fetchall()}

        changes = []

        # Compare rows in the old table with the new table
        for pk, old_row in old_rows.items():
            new_row = new_rows.get(pk)
            if not new_row:
                continue  # Row deleted in the new table
            for i, old_val in enumerate(old_row):
                if i < len(new_columns):
                    new_val = new_row[i]
                    if old_val != new_val:
                        changes.append((table, primary_key_column, pk, new_columns[i], new_val))

        # Check for new rows added in the new table
        for pk, new_row in new_rows.items():
            if pk not in old_rows:
                for i, val in enumerate(new_row):
                    changes.append((table, primary_key_column, pk, new_columns[i], val))

        # Check for new columns added in the new table
        for new_col in set(new_columns) - set(old_columns):
            col_index = new_columns.index(new_col)
            for pk, new_row in new_rows.items():
                null_words = ['', 'none', 'None', 'NONE', 'null']
                if new_row[col_index] not in null_words:
                    changes.append((table, primary_key_column, pk, new_col, new_row[col_index]))

        all_changes.extend(changes)

    # Close the connections
    old_conn.close()
    new_conn.close()

    return all_changes
'''

'''
def compare_sqlite_dbs(old_db_path, new_db_path):
    # Connect to the SQLite databases
    old_conn = sqlite3.connect(old_db_path)
    new_conn = sqlite3.connect(new_db_path)
    
    # Get a cursor for each database
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    # Get the list of all tables in both databases
    old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    old_tables = set([row[0] for row in old_cursor.fetchall()])
    new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    new_tables = set([row[0] for row in new_cursor.fetchall()])
    
    # Find tables that are in both databases
    common_tables = old_tables.intersection(new_tables)
    all_changes = []

    for table in common_tables:
        # Get column info for both old and new tables
        old_cursor.execute(f"PRAGMA table_info({table})")
        old_columns = [info[1] for info in old_cursor.fetchall()]
        new_cursor.execute(f"PRAGMA table_info({table})")
        new_columns = [info[1] for info in new_cursor.fetchall()]
        primary_key = old_columns[0] if old_columns else new_columns[0]

        # Fetch all rows from old and new tables
        old_cursor.execute(f"SELECT * FROM {table}")
        old_rows = {row[0]: row for row in old_cursor.fetchall()}
        new_cursor.execute(f"SELECT * FROM {table}")
        new_rows = {row[0]: row for row in new_cursor.fetchall()}

        changes = []

        # Compare rows in the old table with the new table
        for pk, old_row in old_rows.items():
            new_row = new_rows.get(pk)
            if not new_row:
                continue  # Row deleted in the new table
            for i, old_val in enumerate(old_row):
                if i < len(new_columns):
                    new_val = new_row[i]
                    if old_val != new_val:
                        changes.append((table, pk, old_columns[i], new_val))

        # Check for new rows added in the new table
        for pk, new_row in new_rows.items():
            if pk not in old_rows:
                for i, val in enumerate(new_row):
                    changes.append((table, pk, new_columns[i], val))

        # Check for new columns added in the new table
        for new_col in set(new_columns) - set(old_columns):
            col_index = new_columns.index(new_col)
            for pk, new_row in new_rows.items():
                changes.append((table, pk, new_col, new_row[col_index]))

        all_changes.extend(changes)

    # Close the connections
    old_conn.close()
    new_conn.close()

    return all_changes
'''

def compare_sqlite_dbs(old_db_path, new_db_path):
    # Connect to the SQLite databases
    old_conn = sqlite3.connect(old_db_path)
    new_conn = sqlite3.connect(new_db_path)
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    old_tables = set(row[0] for row in old_cursor.fetchall())
    new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    new_tables = set(row[0] for row in new_cursor.fetchall())
    
    common_tables = old_tables.intersection(new_tables)
    all_changes = []
    for table in common_tables:
        # Get primary key column for the old table
        old_cursor.execute(f"PRAGMA table_info(\"{table}\")")
        old_info = old_cursor.fetchall()
        old_columns = [info[1] for info in old_info]
        old_primary_key = [info[1] for info in old_info if info[5] == 1]  # Column with pk flag (1)
        
        # Get primary key column for the new table
        new_cursor.execute(f"PRAGMA table_info(\"{table}\")")
        new_info = new_cursor.fetchall()
        new_columns = [info[1] for info in new_info]
        new_primary_key = [info[1] for info in new_info if info[5] == 1]  # Column with pk flag (1)

        # If primary key column is not found, default to the first column
        primary_key_column = old_primary_key[0] if old_primary_key else (new_primary_key[0] if new_primary_key else old_columns[0])

        # Fetch all rows from old and new tables
        old_cursor.execute(f"SELECT * FROM \"{table}\"")
        old_rows = {row[old_columns.index(primary_key_column)]: row for row in old_cursor.fetchall()}
        new_cursor.execute(f"SELECT * FROM \"{table}\"")
        new_rows = {row[new_columns.index(primary_key_column)]: row for row in new_cursor.fetchall()}

        changes = []

        # Compare rows in the old table with the new table
        _id = 0
        for pk, old_row in old_rows.items():
            new_row = new_rows.get(pk)
            if not new_row:
                continue  # Row deleted in the new table
            for i, old_val in enumerate(old_row):
                column_name = old_columns[i]
                if column_name in new_columns:
                    new_col_idx = new_columns.index(column_name)
                    new_val = new_row[new_col_idx]
                    '''
                    changes.append((table, primary_key_column, pk, new_columns[i], new_val))
                    '''
                    if old_val != new_val and new_val not in NULL_WORDS:
                        # print("LINE ID ", _id)
                        changes.append((table, primary_key_column, str(pk), new_columns[i], str(new_val)))
            _id += 1
   
        # Check for new rows added in the new table
        _id = 0
        for pk, new_row in new_rows.items():
            if pk not in old_rows:
                for i, val in enumerate(new_row):
                    '''
                    changes.append((table, primary_key_column, pk, new_columns[i], val))
                    '''
                    if val not in NULL_WORDS:
                        # print("LINE ID ", _id)
                        changes.append((table, primary_key_column, str(pk), new_columns[i], str(val)))
            _id += 1
      
        # Check for new columns added in the new table
        for new_col in set(new_columns) - set(old_columns):
            col_index = new_columns.index(new_col)
            _id = 0
            for pk, new_row in new_rows.items():
                '''
                changes.append((table, primary_key_column, pk, new_col, new_row[col_index]))
                '''
                if new_row[col_index] not in NULL_WORDS:
                    # print("LINE ID ", _id)
                    changes.append((table, primary_key_column, str(pk), new_col, str(new_row[col_index])))
                _id += 1
        all_changes.extend(changes)

    old_conn.close()
    new_conn.close()

    return all_changes



def evaluate_model_output_micro_f1(input_path, model_output_path, groundtruth_path, filenames=None):
    all_true_positives, all_false_positives, all_false_negatives = 0, 0, 0
    if filenames is None:
        filenames = load_filenames(model_output_path)
    
    for filename in filenames:
        input_db_path = os.path.join(input_path, filename, 'input.sqlite')
        model_output_db_path = os.path.join(model_output_path, filename, 'output.sqlite')
        groundtruth_db_path = os.path.join(groundtruth_path, filename, 'output.sqlite')
        
        # Get the difference triples between the input database and the model's output
        model_changes = compare_sqlite_dbs(input_db_path, model_output_db_path)
        model_changes_set = set(model_changes)

        # Get the difference triples between the input database and the groundtruth database
        groundtruth_changes = compare_sqlite_dbs(input_db_path, groundtruth_db_path)
        groundtruth_changes_set = set(groundtruth_changes)
        print(len(groundtruth_changes))
        '''
        print(model_changes)
        print(groundtruth_changes)
        print()
        '''
        
        # Calculate precision, recall, and F1 score
        true_positives = len(model_changes_set.intersection(groundtruth_changes_set))
        false_positives = len(model_changes_set - groundtruth_changes_set)
        false_negatives = len(groundtruth_changes_set - model_changes_set)

        all_true_positives += true_positives
        all_false_positives += false_positives
        all_false_negatives += false_negatives
        

    precision = all_true_positives / (all_true_positives + all_false_positives) if all_true_positives + all_false_positives > 0 else 0
    recall = all_true_positives / (all_true_positives + all_false_negatives) if all_true_positives + all_false_negatives > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

# Example usage: evaluate the model using 'input_db.sqlite', 'model_output_db.sqlite', and 'groundtruth_db.sqlite'
# evaluation_metrics = evaluate_database_update_model('input_db.sqlite', 'model_output_db.sqlite', 'groundtruth_db.sqlite')


# Example usage with two SQLite files: 'old_db.sqlite' and 'new_db.sqlite'
# changes = compare_sqlite_dbs('/shared/data2/yizhuj2/text2db/dataset/wiki/116_rp/input.sqlite', '/shared/data2/yizhuj2/text2db/dataset/wiki/116_rp/output.sqlite')
# print(changes)



def evaluate_model_output(input_path, model_output_path, groundtruth_path, filenames=None):
    all_true_positives, all_false_positives, all_false_negatives = 0, 0, 0
    if filenames is None:
        filenames = load_filenames(model_output_path)
    
    pre_list, rec_list, f1_list = [], [], []

    for filename in filenames:
        input_db_path = os.path.join(input_path, filename, 'input.sqlite')
        model_output_db_path = os.path.join(model_output_path, filename, 'output.sqlite')
        groundtruth_db_path = os.path.join(groundtruth_path, filename, 'output.sqlite')
        
        # Get the difference triples between the input database and the model's output
        model_changes = compare_sqlite_dbs(input_db_path, model_output_db_path)
        model_changes_set = set(model_changes)

        # Get the difference triples between the input database and the groundtruth database
        groundtruth_changes = compare_sqlite_dbs(input_db_path, groundtruth_db_path)
        groundtruth_changes_set = set(groundtruth_changes)
        print("Number of New Values: ", len(groundtruth_changes))
        print("Groundtruth: ", groundtruth_changes)
        print("Model Output: ", model_changes)
        print()
        
        
        # Calculate precision, recall, and F1 score
        true_positives = len(model_changes_set.intersection(groundtruth_changes_set))
        false_positives = len(model_changes_set - groundtruth_changes_set)
        false_negatives = len(groundtruth_changes_set - model_changes_set)


        precision = true_positives / (true_positives + false_positives) if true_positives + false_positives > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if true_positives + false_negatives > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0

        pre_list.append(precision)
        rec_list.append(recall)
        f1_list.append(f1_score)


    return {
        'precision': sum(pre_list)/len(pre_list),
        'recall': sum(rec_list)/len(rec_list) ,
        'f1_score': sum(f1_list)/len(f1_list) 
    }
