import os
import json

# import requests #type:ignore
import hashlib


def create_unique_hash(url, params=None, cache_dir="api_cache"):
    key = url + json.dumps(params or {}, sort_keys=True)
    file_name = hashlib.md5(key.encode()).hexdigest() + ".json"
    return os.path.join(cache_dir, file_name)


def get_cached_response(url, params=None, cache_dir="api_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    file_path = create_unique_hash(url, params, cache_dir)

    # Return cached data if exists
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return None


def cache_response(
    data: list | dict, url: str, params: dict = None, cache_dir: str = "api_cache"
) -> None:
    file_path = create_unique_hash(url, params, cache_dir)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# def get_cached_response(url, params=None, cache_dir="api_cache"):
#     os.makedirs(cache_dir, exist_ok=True)
#     file_path = create_unique_hash(url,params,cache_dir)

#     # Return cached data if exists
#     if os.path.exists(file_path):
#         with open(file_path, "r", encoding="utf-8") as f:
#             return json.load(f)

#     # Otherwise, make the request and cache it
#     response = requests.get(url, params=params)
#     response.raise_for_status()
#     data = response.json()

#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     return data
