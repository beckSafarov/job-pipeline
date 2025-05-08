from utils.common_utils import (
    map_ids_to_dicts,
    map_ids_to_nested_dicts,
    remove_empty_dicts,
    remove_empty_lists,
    flatten,
    is_empty_list,
)


def prep_dict_lists(ids:list, data:list)->list:
    """prepares dicts to load to db

    Args:
        ids (list): e.g. [1,2,3,4,...]
        data (list): e.g. [{}, {'from': None, 'to': 39000000, 'currency': 'UZS'}, {}]

    Returns:
        list: e.g. [{'id':1, 'from': None, 'to': 39000000, 'currency': 'UZS'}]
    """
    if is_empty_list(ids) or is_empty_list(data):
      return  
    mapped_to_ids = map_ids_to_dicts(ids,data)
    return remove_empty_dicts(mapped_to_ids)

def prep_nested_lists(ids:list, data:list)->list:
  """prepares nested lists to load to db

  Args:
      ids (list): e.g. [1,2,3,4,...]
      data (list): e.g. [[{'name':'Python'},{'name':'Excel'}],...,[]]

  Returns:
      list: e.g. [{'id': 1, 'name': "Python"},{'id':1, 'name':'Excel'},...]
  """
  if is_empty_list(ids) or is_empty_list(data):
    return  
  mapped_to_ids = map_ids_to_nested_dicts(ids,data)
  empty_lists_removed = remove_empty_lists(mapped_to_ids)
  return flatten(empty_lists_removed)
