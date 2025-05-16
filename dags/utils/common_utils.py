import json
from itertools import chain
from config import API


def is_empty_dict(item: dict) -> bool:
    return len(list(item.keys())) < 1


def is_empty_list(item: list) -> bool:
    return len(item) < 1


def remove_empty_dicts(data: list) -> list:
    return [item for item in data if is_empty_dict(item) == False]


def remove_empty_lists(data: list) -> list:
    return [item for item in data if len(item) > 0]


def flatten(data: list) -> list:
    return list(chain(*data))


def is_invalid_item(item):
    return type(item) is not dict or len(list(item.keys())) < 1


def filter_dicts_without_prop(data: list, prop: str):
    return [item for item in data if prop in item]


def map_ids_to_nested_dicts(ids: list, data: list, key_name: str = "job_id") -> list:
    for i, reqs_from_single_post in enumerate(data):
        if is_empty_list(reqs_from_single_post) or ids[i] is None:
            continue
        curr_job_id = ids[i]
        for req in reqs_from_single_post:
            if is_invalid_item(req):
                continue
            req[key_name] = curr_job_id
    return data


def map_ids_to_dicts(ids: list, data: list, key_name: str = "job_id") -> list:
    for i, record in enumerate(data):
        if is_invalid_item(record) or is_empty_dict(record) or ids[i] == None:
            continue
        record[key_name] = ids[i]
    return data


def write_json(data: dict | list, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f)


def get_json(path: str):
    with open(path, "r") as f:
        return json.load(f)


def get_files_from_paths(paths: list):
    files = []
    for path in paths:
        files.append(get_json(path))
    return files


from urllib.parse import urlencode, urlunparse


def build_encoded_hh_url(params):
    """
    Given a base URL and query params, returns a properly URL-encoded HH API request URL.
    """
    split_api = API.split("/")
    scheme, netloc, path = "https", split_api[2], split_api[3]

    # Encode query parameters
    query_string = urlencode(params, safe=":")

    if "date_from" in params:
        params["date_from"].replace("+03", "+05")

    # Construct full URL
    return urlunparse((scheme, netloc, path, "", query_string, ""))
