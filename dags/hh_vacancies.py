from airflow.decorators import (  # type:ignore
    dag,
    task,
)  # This DAG uses the TaskFlow API. See: https://www.astronomer.io/docs/learn/airflow-decorators
from pendulum import datetime, duration #type: ignore
from utils.hh_api import get_vacancy_details, get_latest_vacancies  # type: ignore
from utils.split_vac_data import split_vac_data
import time  # type: ignore
from dags.utils.insert_to_db import insert_to_table
from utils.common_utils import (
    get_files_from_paths,
    get_json,
    write_json,
)
from utils.prep_to_db import prep_dict_lists, prep_nested_lists
from data.data import roles
from utils.db_utils import query_latest_vacancy
from utils.filter_utils import is_vac_fresh


@dag(
    start_date=datetime(2025, 1, 1),  # date after which the DAG can be scheduled
    schedule="@daily",  # see: https://www.astronomer.io/docs/learn/scheduling-in-airflow for options
    catchup=False,  # see: https://www.astronomer.io/docs/learn/rerunning-dags#catchup
    max_consecutive_failed_dag_runs=5,  # auto-pauses the DAG after 5 consecutive failed runs, experimental
    doc_md=__doc__,  # add DAG Docs in the UI, see https://www.astronomer.io/docs/learn/custom-airflow-ui-docs-tutorial
    default_args={
        "owner": "Astro",  # owner of this DAG in the Airflow UI
        "retries": 3,  # tasks retry 3 times before they fail
        "retry_delay": duration(seconds=5),  # tasks wait 30s in between retries
    },  # default_args are applied to all tasks in a DAG
    tags=["hh", "vacancies"],  # add tags in the UI
    is_paused_upon_creation=False,  # start running the DAG as soon as its created
)

def hh_vacancies():

    @task
    def fetch_latest_publication():
        latest_vacancy = query_latest_vacancy()
        published_at = latest_vacancy.get("published_at", {}).isoformat()
        return published_at

    @task
    def fetch_basic_vacancies(published_at: str) -> str:
        """
        This task uses the requests library to retrieve a list of vacancies
        currently available at HH. The results are pushed to XCom with a specific key
        so they can be used in a downstream pipeline. The task returns a list
        of vacancies to be used in the next task.
        The function makes an API call to the HH API and returns the number of vacancies
        as a JSON response. The function also handles any exceptions that may occur
        during the API call and returns an empty list if an error occurs.
        Args:
            context (dict): The context dictionary passed to the task.
        Returns:
            list[dict]: A list of vacancies currently available at HH.
        """
        role_ids = [role["id"] for role in roles]
        # role_ids = [96]
        all_vacancies = []
        for role_id in role_ids:
            role_vacs = get_latest_vacancies(published_at, role_id)
            all_vacancies.extend(role_vacs)
        file_path = "/tmp/vacancies.json"
        write_json(all_vacancies, file_path)
        return file_path

    @task
    def filter_old_vacancies(path: str, latest_publish: str) -> str:
        vacancies = get_json(path)
        latest_it_vacancies = []
        for vac in vacancies:
            is_fresh_vac = is_vac_fresh(latest_publish, vac["published_at"])
            if is_fresh_vac is False:
                continue
            latest_it_vacancies.append(vac)
        write_path = "/tmp/filtered_vacancies.json"
        write_json(latest_it_vacancies, write_path)
        return write_path

    @task
    def fetch_detailed_vacancies(path: str) -> str:
        vacancies = get_json(path)

        for vacancy in vacancies:   
            vacancy_id = vacancy["id"]
            vacancy_details = get_vacancy_details(vacancy_id)
            if vacancy_details:
                vacancy["description"] = vacancy_details.get("description", "")
                vacancy["key_skills"] = vacancy_details.get("key_skills", [])
                vacancy["languages"] = vacancy_details.get("languages", [])
            else:
                print(f"Error fetching details for vacancy ID {vacancy_id}")
            time.sleep(0.2)  # Add a small delay to be nice to the API

        file_path = "/tmp/vacancy_details.json"
        write_json(vacancies, file_path)
        return file_path

    @task
    def transform_and_split_data(path: str) -> list:
        """ """
        vacancies = get_json(path)
        if vacancies is None:
            print("No vacancies found.")
            return

        tables = split_vac_data(vacancies)
        paths = []

        for table_name in tables.keys():
            table_path = f"/tmp/{table_name}.json"
            paths.append(table_path)
            write_json(tables[table_name], table_path)
        return paths

    @task
    def load_to_db(paths:list)->None:
        if len(paths) < 1:
            print("Paths is empty")
            return 

        jobs, employers, addresses, salaries, job_languages, job_roles, job_skills = (
            get_files_from_paths(paths)
        )
        insert_to_table("Employer", employers)
        job_ids = insert_to_table("Job", jobs)
        salaries_with_ids = prep_dict_lists(job_ids, salaries)
        addresses_with_ids = prep_dict_lists(job_ids, addresses)
        job_roles_with_ids = prep_nested_lists(job_ids, job_roles)
        job_skills_with_ids = prep_nested_lists(job_ids, job_skills)
        job_languages_with_ids = prep_nested_lists(job_ids, job_languages)
        insert_to_table("Address", addresses_with_ids)
        insert_to_table("Salary", salaries_with_ids)
        insert_to_table("JobLanguage", job_languages_with_ids)
        insert_to_table("JobRole", job_roles_with_ids)
        insert_to_table("JobSkill", job_skills_with_ids)
        return None

    @task
    def print_test(paths: list):
        # vacancies = get_json(path)
        jobs, employers, addresses, salaries, job_languages, job_roles, job_skills = (
            get_files_from_paths(paths)
        )
        print(jobs)
        return salaries

    published_at = fetch_latest_publication()
    basic_vacancies_path = fetch_basic_vacancies(published_at)
    filtered_vacs_path = filter_old_vacancies(basic_vacancies_path, published_at)
    path_to_detailed_vacancies_file = fetch_detailed_vacancies(filtered_vacs_path)
    paths_to_tables = transform_and_split_data(path_to_detailed_vacancies_file)
    load_to_db(paths_to_tables)


# Instantiate the DAG
hh_vacancies()
