import json
from itertools import chain

def is_empty_dict(item:dict)->bool:
  return len(list(item.keys())) < 1

def is_empty_list(item:list)->bool:
  return len(item) < 1

def remove_empty_dicts(data:list)->list:
  return [item for item in data if is_empty_dict(item) == False]

def remove_empty_lists(data:list)->list:
  return [item for item in data if len(item) > 0]

def flatten(data:list)->list:
  return list(chain(*data))

def map_ids_to_nested_dicts(ids: list, data: list, key_name:str = 'job_id')->list:
    for i,reqs_from_single_post in enumerate(data):
        if is_empty_list(reqs_from_single_post):
          continue
        curr_job_id = ids[i]
        for req in reqs_from_single_post:
            req[key_name] = curr_job_id

    return data

def map_ids_to_dicts(ids: list, data: list, key_name:str = 'job_id')->list:
    for i, record in enumerate(data):
        if is_empty_dict(record):
            continue
        record[key_name] = ids[i]
    return data


def get_json(path: str):
    with open(path, "r") as f:
        return json.load(f)


def get_files_from_paths(paths: list):
    files = []
    for path in paths:
        files.append(get_json(path))
    return files
