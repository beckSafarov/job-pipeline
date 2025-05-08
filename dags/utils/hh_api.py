import requests # type: ignore
import time
# from utils.cache_utils import get_cached_response,cache_response
API = "https://api.hh.ru/vacancies"


def get_vacancies_by_page(page=1, role_id=10, country_id=97):
    url = f"{API}?area={country_id}&professional_role={role_id}"
    url = url if page <= 1 else url + f"&page={page}"
    # params = {"area": country_id, "professional_role": role_id}
    # cached_response = get_cached_response(API, params)
    # if cached_response is not None:
    #     return cached_response

    # print(f"does cached response exist for basic vacancies: {bool(cached_response)}")
    try:
        r = requests.get(url)
        data = r.json()
        # cache_response(data, API, params)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None


def get_all_vacancies(country_id, role_id):
    # Get first page and initialize variables
    json_data = get_vacancies_by_page(1, role_id, country_id)
    
    if not json_data:
        print("Error fetching data from API")
        return []

    pages = json_data["pages"]
    overall_jobs = json_data["found"]
    jobs = json_data["items"]

    print(f"Total jobs found: {overall_jobs}")
    print(f"Total pages to fetch: {pages}")

    # Fetch remaining pages
    if pages > 1:
        for i in range(1, pages):
            more_jobs = get_vacancies_by_page(i + 1,role_id,country_id)
            
            if more_jobs:
                jobs.extend(more_jobs["items"])
            else:
                print("Fetch page number error")
            # Add a small delay to be nice to the API
            time.sleep(0.2)  # Increased delay slightly

    return jobs


def get_vacancy_details(vacancy_id):
    url = f"{API}/{vacancy_id}"
    # cached_response = get_cached_response(url)
    # if cached_response is not None:
    #     return cached_response

    # print(f"does cached response exist for vacancy details: {bool(cached_response)}")
    try:
        r = requests.get(url)
        data = r.json()
        # cache_response(data, url)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return None
    except KeyError as e:   
        print(f"Key error in JSON response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
