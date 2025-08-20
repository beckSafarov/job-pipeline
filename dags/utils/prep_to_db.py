from utils.common_utils import (
    map_ids_to_dicts,
    map_ids_to_nested_dicts,
    remove_empty_dicts,
    remove_empty_lists,
    flatten,
    is_empty_list,
    filter_dicts_without_prop,
)


def prep_dict_lists(ids: list, data: list, id_column="job_id") -> list:
    """prepares dicts to load to db

    Args:
        ids (list): e.g. [1,2,3,4,...]
        data (list): e.g. [{}, {'from': None, 'to': 39000000, 'currency': 'UZS'}, {}]

    Returns:
        list: e.g. [{'id':1, 'from': None, 'to': 39000000, 'currency': 'UZS'}]
    """
    # print("ids below")
    # print(ids)
    # print("data below")
    # print(data)
    if is_empty_list(ids) or is_empty_list(data):
        return
    mapped_to_ids = map_ids_to_dicts(ids,data)
    # print("mapped to ids below")
    # print(mapped_to_ids)
    filtered = filter_dicts_without_prop(mapped_to_ids, id_column)
    # print("filtered below")
    # print(filtered)
    return filtered


def prep_nested_lists(ids: list, data: list, id_column="job_id") -> list:
    """prepares nested lists to load to db

    Args:
        ids (list): e.g. [1,2,3,4,...]
        data (list): e.g. [[{'name':'Python'},{'name':'Excel'}],...,[]]
        id_column (str): column name to use for the ID (default: "job_id")

    Returns:
        list: e.g. [{'id': 1, 'name': "Python"},{'id':1, 'name':'Excel'},...]
    """
    if is_empty_list(ids) or is_empty_list(data):
        return
    mapped_to_ids = map_ids_to_nested_dicts(ids, data)
    empty_lists_removed = remove_empty_lists(mapped_to_ids)
    flattened = flatten(empty_lists_removed)
    filtered = filter_dicts_without_prop(flattened, id_column)
    return filtered
