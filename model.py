import os
import re
import sys
import json
import copy
from util import *
from ie_tools import *
import prompt_library.planner, prompt_library.analyzer
import prompt_library.tools.re, prompt_library.tools.ner, prompt_library.tools.ae, prompt_library.tools.classification, prompt_library.tools.norm
import traceback



class solver:
    def __init__(self, args):
        self.api_key = args.api_key
        self.gpt_version = args.gpt_version
        self.data_file_name = args.data_file_name
        self.demo_file_name = args.demo_file_name
        self.cache = {}
    

    def solve(self, data, max_revise_times=10, max_rerun_times=3, task_type=None):
        instruction = data['instruction']
        docs = data['docs']
        database_schema = data['db_schema']
        raw_database = data['db_data']
        print('Database schema:')
        print(database_schema)
        print('Instruction:')
        print(instruction)
        print('Text:')
        print(data['text'][:500] + '...')
        print('Number of docs:')
        print(len(docs))
        print()
        

        # get the module input
        demo_prompt = prompt_library.planner.prompt[task_type]
        test_prompt = f"Instruction: {data['instruction']}\n\nDatabase schema: {data['db_schema']}\n\n" # test prompt
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt
        

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
        
        code_version = []
        while max_rerun_times: 
            revise_times = 0
            error_message = None
            code_version = []
            while revise_times < max_revise_times:
                print(revise_times, "attempt:")
                # [1] Generate the code
                code = self.generate_code(messages)
                if code.startswith('Output:'):
                    code = code.replace('Output:', '').strip()
                code_version.append(code)
                print("Generated code: ")
                print(code)
                print('----------------------')
                database = copy.deepcopy(raw_database)
                # [2] Execute the code 
                if_success = True
                for i, doc in enumerate(docs):
                    text = doc[:3000]
                    error_message, database = self.execute_code(code, instruction, text, database_schema, database)
                    if error_message:
                        if len(messages) == 2:
                            messages += [{}, {}]
                        messages[2] = {"role": "system", "content": code}
                        messages[3] = {"role": "user", "content": "Please revise the code according to the error message. Don't apologize. Don't output any extra information. Just output the new complete executable code:\n" + error_message}
                        revise_times += 1
                        if_success = False        
                        print("Failed...")
                        print(error_message)
                        print()
                        break
                    else:
                        print(f"Successfully for Doc {i}!!!")
                if if_success:
                    return True, code_version, database
            max_rerun_times -= 1
        return False, code_version, raw_database


    
    def generate_code(self, messages):
        return get_chat_response(messages, self.api_key, self.gpt_version)
        

    def execute_code(self, code_string, instruction, text, database_schema, database):
        message = ""
        try:
            # Execute the provided code string
            exec(code_string)
        except Exception:
            # Print the traceback of the exception if an error occurs
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)

            # Retrieve the last traceback object and extract the line number
            tb = traceback.extract_tb(exc_traceback)[-1]
            line_number = tb.lineno

            # Print the error message and the line of code that caused the error
            message += f"Error message: \n{exc_value}\n\n"
            try:
                # Split the code by lines and print the one that caused the error
                lines = code_string.split('\n')
                error_line = lines[line_number - 1]  # Adjust for 0-based index
                message += f"Error occured in the following codes: \n{error_line.strip()}\n"
            except IndexError:
                message += "Error line not found in the provided code string.\n"
        else:
            # If no exception occurs, print no error message
            message = ""
        return message, database

    def analyze_db(self, db_schema, db_data, num_used_data=20, rerun_times=5):
        table_schemas = db_schema.strip().split("\n\n")
        for schema in table_schemas:
            obj_type, obj_name, obj_sql = parse_schema_details(schema)
            demo_prompt = prompt_library.analyzer.prompt
            test_prompt = f"Database schema: {schema}\n\nExisting data entries: \n" # test prompt
            for i in range(num_used_data):
                values = list(db_data[obj_name][i].values())
                test_prompt += ('\t'.join(values)) + "\n"
            full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt
            print(full_prompt)

            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ]
            
            num_col = len(db_data[obj_name][0])
            times = 0
            while times < rerun_times: 
                string = get_chat_response(messages, self.api_key, self.gpt_version)
                if string.startswith('Output:'):
                    string = string.replace('Output:', '').strip()
                hints = string.split('\n')
                if len(hints) == num_col:
                    break
                times += 1

            
         





