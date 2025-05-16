from utils.date_utils import is_earlier

def is_vac_fresh(latest_publish: str, curr_published_date:str)->bool:
  """is current vacancy later than the latest available vacancy

  Args:
      latest_publish (str): latest publishing date of an existing vacancy
      curr_published_date (str): publishing date of the current vacancy

  Returns:
      bool: yes or no, no -> negative
  """
  vac_pub_date = curr_published_date.replace("+0300", "+0500")
  return is_earlier(latest_publish, vac_pub_date)