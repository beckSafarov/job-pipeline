import json

def get_json(path:str):
    with open(path, "r") as f:
        return json.load(f)



def get_files_from_paths(paths:list):
    files = []
    for path in paths:
        files.append(get_json(path))
    return files