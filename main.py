
import os
import sys
import json
import argparse
import sqlite3
import random
from tqdm import tqdm
import traceback

from util import *
from model import solver
from evaluate import compare_sqlite_dbs, evaluate_model_output

YOUR_API_KEY = os.environ.get("OPENAI_API_KEY")



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_root', type=str, default='./dataset')
    parser.add_argument('--data_file_name', type=str, default='data.json')
    parser.add_argument('--demo_file_name', type=str, default='demonstration.json')
    parser.add_argument('--output_root', type=str, default='./output')
    parser.add_argument('--api_key', type=str, default=YOUR_API_KEY)
    parser.add_argument('--gpt_version', type=str, default='gpt-4')
    parser.add_argument('--max_revise_times', type=int, default=10)
    parser.add_argument('--max_rerun_times', type=int, default=3)
    
    args = parser.parse_args()

    print('====Input Arguments====')
    print(json.dumps(vars(args), indent=2, sort_keys=False))
    return args


if __name__ == "__main__":
    args = parse_args()
    solver = solver(args)
    filenames = load_filenames(args.data_root)
    #filenames = ['bird_33_rp']

    print(filenames)
    print(f"# Number of test data: {len(filenames)}\n")
    
    success_times = 0
    for filename in tqdm(filenames):
        path = os.path.join(args.data_root, filename)
        print(path)
        # [1] Load the data
        data = load_data(path)
        task_type = path[-2:]

		# [2] Update the database
        if_success, code_version, database = solver.solve(data, args.max_revise_times, args.max_rerun_times, task_type)
        
        # [3] Save the database
        output_path = os.path.join(args.output_root, filename) 
        save_data(output_path, database, code_version if if_success else None)
        
        # [4] Evaluate the model output
        changes = compare_sqlite_dbs(os.path.join(path, 'input.sqlite'), os.path.join(output_path, 'output.sqlite'))
        print(changes)
        success_times += int(if_success)
    print("Success rate: ", success_times/len(filenames))

    
    eval_scores = evaluate_model_output(args.data_root, args.output_root, args.data_root, filenames)
    print("Evaluation scores: ", eval_scores)
    
    
