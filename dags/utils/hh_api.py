import requests # type: ignore
import time
from utils.common_utils import build_encoded_hh_url
from config import API


def get_vacancies_by_page_and_role(page=1, role_id=10, country_id=97):
    url = f"{API}?area={country_id}&professional_role={role_id}"
    url = url if page <= 1 else url + f"&page={page}&per_page=100"
    try:
        r = requests.get(url)
        data = r.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None


def get_latest_vacancies_by_page(date_from: str, role: int, page=0, country_id=97):
    url = build_encoded_hh_url(
        {
            "area": country_id,
            "page": page,
            "date_from": date_from,
            "per_page": 100,
            "professional_role": role,
        }
    )

    try:
        r = requests.get(url)
        data = r.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None


def get_latest_vacancies(date_from: str, role_id: int, country_id: int = 97) -> list:
    # Get first page and initialize variables
    json_data = get_latest_vacancies_by_page(date_from, role_id)

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
            more_jobs = get_latest_vacancies_by_page(date_from, role_id, i + 1)

            if more_jobs:
                jobs.extend(more_jobs["items"])
            else:
                print("Fetch page number error")
            # Add a small delay to be nice to the API
            time.sleep(0.2)  # Increased delay slightly

    return jobs


def get_all_vacancies(country_id: int, role_id: int) -> list:
    # Get first page and initialize variables
    json_data = get_vacancies_by_page_and_role(1, role_id, country_id)

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
            more_jobs = get_vacancies_by_page_and_role(i + 1, role_id, country_id)

            if more_jobs:
                jobs.extend(more_jobs["items"])
            else:
                print("Fetch page number error")
            # Add a small delay to be nice to the API
            time.sleep(0.2)  # Increased delay slightly

    return jobs


def get_vacancy_details(vacancy_id):
    url = f"{API}/{vacancy_id}"
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
