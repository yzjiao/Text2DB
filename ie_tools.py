import os
import re
import sys
import json
import copy
from util import *
import prompt_library.tools.re, prompt_library.tools.ner, prompt_library.tools.ae, prompt_library.tools.classification, prompt_library.tools.norm
import traceback
import pickle
import sys

sys.path.append("./GENRE")
sys.path.append("./GENRE/fairseq")

from genre.trie import Trie
from genre.fairseq_model import GENRE
from genre.entity_linking import get_end_to_end_prefix_allowed_tokens_fn_fairseq as get_prefix_allowed_tokens_fn
from genre.utils import get_entity_spans_fairseq as get_entity_spans
GENRE_model = GENRE.from_pretrained("./GENRE/models/fairseq_e2e_entity_linking_aidayago").eval().to("cuda:0")
NULL_WORDS = ['', 'none', 'None', 'NONE', 'null', 'NULL', 'Null', 'Unknown', 'unknown', None]
            

@enforce_types
def Named_Entity_Recognition(text: str, type: str) -> list:
    print("running Named_Entity_Recognition")
    demo_prompt = prompt_library.tools.ner.prompt.strip()
    test_prompt = f"Text: {text}\n\nType: {type}\n\n"
    full_prompt = demo_prompt + "\n\n" + test_prompt
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
    # execute the module
    res = get_chat_response(messages)
    entity_list = res.split('\n')
    entity_list = list(set(entity_list))
    entity_list = [e for e in entity_list if e not in NULL_WORDS]
    print(entity_list)
    return entity_list


@enforce_types
def Relation_Extraction(text: str, head_e:list, relation: str) -> list: 
    # print("running Relation_Extraction")
    demo_prompt = prompt_library.tools.re.prompt.strip()
    test_prompt = f"Text: {text}\n\nHead entity: {head_e}\n\nRelation: {relation}\n\n"
    full_prompt = demo_prompt + "\n\n" + test_prompt
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
    # execute the module
    res = get_chat_response(messages)
    tail_entity_list = res.split('\n')
    # print(tail_entity_list)
    return tail_entity_list


@enforce_types
def Attribute_Extraction(text: str, entity: str, attribute_list: list) -> dict: 
    # print("running Attribute_Extraction")
    demo_prompt = prompt_library.tools.ae.prompt.strip()
    attribute_list_str = '\n'.join(attribute_list)
    test_prompt = f"Text: {text}\n\nEntity: {entity}\n\nAttribute Names: {attribute_list_str}\n\n\n"
    full_prompt = demo_prompt + "\n\n\n" + test_prompt
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
    # execute the module
    print("Attribute_Extraction")
    print(f"Entity: {entity}\n\nAttribute Names: {attribute_list_str}\n\n\n")
    dic = {}
    running_time = 3
    while running_time:
        res = get_chat_response(messages)
        print(res)
        values = res.strip().split('\n')
        if len(values) == len(attribute_list):
            for k, v in zip(attribute_list, values):
                dic[k] = v
            break
        else:
            running_time -= 1
    assert len(dic) == len(attribute_list), f"The number of generated values are different from the number of attribute names."
    # print(dic)
    return dic



@enforce_types
def Text_Classification(text: str, label_list: list) -> str: 
    # print("running Text_Classification")
    demo_prompt = prompt_library.tools.classification.prompt.strip()
    test_prompt = f"Text: {text}\n\Label list: {', '.join(label_list)}\n\n"
    full_prompt = demo_prompt + "\n\n" + test_prompt
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
    # execute the module
    res = get_chat_response(messages)
    # print(res)
    return res


@enforce_types
def Entity_Linking(data_entries: list, database: dict, table_name: str) -> list:
    print(data_entries) 
    def check_if_list_of_dicts(lst):
        return [isinstance(element, dict) for element in lst]

    def data2text(dictionary, shared_keys):
        parts = [] 
        for key in shared_keys:
            value = dictionary[key]
            if value not in NULL_WORDS:
                parts.append(f"{key}: {value}")
        return ', '.join(parts) + '.'
    

    def extract_bracketed_info_trimmed(sentence):
        # Regular expression to find text within [ ] and trim spaces
        pattern = r"\[\s*(.*?)\s*\]"
        matches = re.findall(pattern, sentence)
        return matches


    def get_shared_keys(data_entries, database, table_name):
        def check_key(dict_list, key):
            for d in dict_list:
                if key not in d or d[key] == '':
                    # print('In check_key function, ', key, d)
                    return False  
            return True 
        db_keys = set(database[table_name][0].keys())
        ref_keys = set(data_entries[0].keys())
        shared_keys = db_keys.intersection(ref_keys)
        target_keys = [key for key in shared_keys if check_key(database[table_name], key)]
        return target_keys


    assert check_if_list_of_dicts(data_entries), f"the input data entries are not a list of dictionaries."
    target_keys = get_shared_keys(data_entries, database, table_name)
    # print('target_keys ', target_keys)
    texts = [data2text(data_entry, target_keys) for data_entry in data_entries]
    db_texts = [data2text(data, target_keys) for data in database[table_name]]
    candidates_dict={text: db_texts for text in texts}
    sentences = ['Here is a piece of data. '+text for text in texts]
    
    prefix_allowed_tokens_fn = get_prefix_allowed_tokens_fn(
        GENRE_model,
        sentences,
        mention_trie=Trie([
            GENRE_model.encode(" {}".format(e))[1:].tolist()
            for e in texts
        ]),
        mention_to_candidates_dict=candidates_dict
    )

    model_res = GENRE_model.sample(
        sentences,
        prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
    )

    index_list = []
    for res_list in model_res:
        index = -1 
        print(res_list)
        for res in res_list:
            linked_text = extract_bracketed_info_trimmed(res['text'])
            if linked_text and linked_text[0] in db_texts:
                index = db_texts.index(linked_text[0])
                break
        index_list.append(index)
    print(index_list)
    return index_list



@enforce_types
def Data_Normalization(data_entries: list, database: dict, table_name: str, data_format: dict = {}, num_example=5, 
delimiter=';  ') -> list: 
    def check_uniform_length(list_of_lists, number=None):
        if number is None:
            number = len(list_of_lists[0])
        # Get the length of the first list
        if not list_of_lists:  # Check if the list of lists is empty
            return False
        # Check if all lists have the same length as the first one
        return all(len(lst) == number for lst in list_of_lists)


    # print("running Data_Normalization")
    assert len(data_entries) > 0, f"the input data entry is an empty list"
    assert check_uniform_length(data_entries)
    last_row = database[table_name][-1]
    db_keys = set(last_row.keys())
    ref_keys = set(data_entries[0].keys())
    if data_format == {}:
        assert ref_keys.issubset(db_keys), f"some attributes from the new data entry doesn't match the {table_name} table. If the task type is column addtion, please define and input the data format."
    
    demo_prompt = prompt_library.tools.norm.prompt.strip()
    data_entry_value = []
    for data_entry in data_entries:
        value_list = [str(data_entry[key]) for key in ref_keys]
        data_str = delimiter.join(value_list)
        data_entry_value.append(data_str)
    new_data_str = '\n'.join(data_entry_value)

    existing_data_str = ''
    for data in database[table_name][(-num_example):]:
        data_value = [str(data[key]) for key in ref_keys if key in data]
        if len(data_value) > 0:
            existing_data_str += delimiter.join(data_value) + '\n'

    test_prompt = f"New data: \n{new_data_str}\n\n"
    if existing_data_str != '':
        test_prompt += f"Existing data: \n{existing_data_str}\n\n"
    if data_format is not None:
        test_prompt += f"Data format requirement: \n{data_format}\n\n"
    full_prompt = demo_prompt + "\n\n" + test_prompt
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
    
    # execute the module
    running_time = 5
    new_data_entries = []
    while running_time:
        res = get_chat_response(messages)
        new_value_list = res.strip().split('\n')
        new_value_list = [values.split(delimiter) for values in new_value_list]
        error_message = ""
        if check_uniform_length(new_value_list, len(ref_keys)):
            for new_values in new_value_list:
                data = {key: value for key, value in zip(ref_keys, new_values)}
                new_data_entries.append(data)
            if len(new_data_entries) == len(data_entries):
                break
            else:
                error_message = f"Wrong. The number of data entries are changed after normalization."
        else: 
            error_message = f"Wrong. The number of values in different data entries are different. Please just output again and do not output any extra words."
        running_time -= 1
        if len(messages) == 2:
            messages += [{}, {}]
        messages[2] = {"role": "system", "content": res}
        messages[3] = {"role": "user", "content": error_message}
    print(data_entries)
    print(new_data_entries)
    print()
    return new_data_entries



@enforce_types
def Infill_Data(data_entry: list, database: dict, table_name: str) -> dict: 
    def check_if_list_of_dicts(lst):
        return [isinstance(element, dict) for element in lst]
    assert check_if_list_of_dicts(data_entry), f"the input data entries are not a list of dictionaries."
    
    db_keys = list(database[table_name][-1].keys())
    ref_keys = list(data_entry[0].keys())
    assert set(ref_keys).issubset(set(db_keys)), f"For data infilling, keys of the new data entry is not a subset of the columns in the {table_name} table."
    index_list = Entity_Linking(data_entry, database, table_name)
    print(index_list)
    for (data, index) in zip(data_entry, index_list):
        if index == -1:
            continue 
        for key in list(data.keys()):
            # since the first key can be primary
            print('existing values:')
            print(database[table_name][index])
            if data[key] not in NULL_WORDS and database[table_name][index][key] in NULL_WORDS:
                database[table_name][index][key] = data[key]
                print('newly-added values:')
                print(database[table_name][index])
                print()
    
    return database



@enforce_types
def Populate_Row(data_entries: list, database: dict, table_name: str) -> dict: 
    def check_if_list_of_dicts(lst):
        return [isinstance(element, dict) for element in lst]
    assert check_if_list_of_dicts(data_entries), f"the input data entries are not a list of dictionaries."
    
    db_keys = list(database[table_name][0].keys())
    ref_keys = list(data_entries[0].keys())
    assert set(ref_keys) == set(db_keys), f"For row population, keys of the new data entry and the {table_name} table do not match."
    for data_entry in data_entries:
        reordered_dict = {key: data_entry.get(key, '') for key in db_keys}
        database[table_name].append(reordered_dict)
    return database


@enforce_types
def Add_Column(data_entry: list, database: dict, table_name: str, new_columns: list, default_value: str='') -> dict: 
    if data_entry == []:
        return database
    def check_if_list_of_dicts(lst):
        return [isinstance(element, dict) for element in lst]
    assert check_if_list_of_dicts(data_entry), f"the input data entries are not a list of dictionaries."
    
    db_keys = list(database[table_name][-1].keys())
    ref_keys = list(data_entry[0].keys())
    # new_columns = set(ref_keys).difference(set(db_keys))

    print('Add_Column')
    print(db_keys)
    print(ref_keys)
    print(new_columns)
    print()
    assert len(new_columns) > 0, f"For column addition, the new data entry doesn't include any new columns compared with the {table_name} table."
    index_list = Entity_Linking(data_entry, database, table_name)
    print(index_list)
    for (data, index) in zip(data_entry, index_list):
        if index == -1:
            continue
        for key in new_columns:
            if data[key] not in NULL_WORDS:
                database[table_name][index][key] = data[key]
    for data in database[table_name]:
        for key in new_columns:
            if key not in data:
                data[key] = default_value
    return database
