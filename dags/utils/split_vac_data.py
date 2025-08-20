def handle_work_format(formats: list) -> str:
    if len(formats) < 1:
        return formats
    format_ids = [format["id"].lower() for format in formats]
    if "on_site" in format_ids and "remote" in format_ids:
        return "hybrid"
    return format_ids[0]


def handle_work_hours(hours: list)->str:
    if len(hours) < 1:
        return hours
    elif len(hours) < 2:
        return hours[0]["id"]
    elif all("HOURS" in s for s in hours):
        hours_numbers = [hour["id"].split("_")[1] for hour in hours]
        return max(hours_numbers)
    return hours[0]['id']


def build_job_data(vacancy: dict) -> dict:
    return {
        "source_id": int(vacancy["id"]),
        "title": vacancy["name"],
        "area_id": int(vacancy["area"]["id"]),
        "employer": int(vacancy["employer"]["id"]),
        "schedule": vacancy["schedule"]["id"],
        "work_format": handle_work_format(vacancy["work_format"]),
        "working_hours": handle_work_hours(vacancy["working_hours"]),
        "employment_form": vacancy["employment_form"]["id"],
        "experience": vacancy["experience"]["id"],
        "is_internship": vacancy["internship"],
        "description": vacancy.get("description", ""),
        "published_at": vacancy["published_at"],
    }


def build_employer_data(vacancy: dict) -> dict:
    return {
        "id": int(vacancy["employer"]["id"]),
        "name": vacancy["employer"]["name"],
        "is_accredited": vacancy["employer"]["accredited_it_employer"],
    }


def build_address_data(vacancy: dict) -> dict:
    if vacancy["address"] is None:
        return {}
    return {
        "lat": float(vacancy["address"]["lat"]),
        "lng": float(vacancy["address"]["lng"]),
        "city": vacancy["address"]["city"],
        "street": vacancy["address"]["street"],
        "building": vacancy["address"]["building"],
    }


def build_languages_data(vacancy: dict) -> list:
    if vacancy["languages"] is None:
        return []
    languages_data = []
    for language in vacancy["languages"]:
        languages_data.append(
            {
                "lang_id": language["id"],
                "lang_level": language["level"]["id"],
            }
        )
    return languages_data


def build_salaries_data(vacancy: dict) -> dict:
    salary_data = {}
    if vacancy["salary"] is not None:
        salary_data = {
            "salary_from": vacancy["salary"]["from"],
            "salary_to": vacancy["salary"]["to"],
            "currency": vacancy["salary"]["currency"],
        }
    return salary_data


def build_job_roles_data(vacancy: dict) -> list:
    # job_roles_data = []
    job_roles_data = []
    if vacancy["professional_roles"] is not None:
        # role = vacancy["professional_roles"][0]
        # job_roles_data = {"source_id": source_id, "role_id": int(role["id"])}
        for role in vacancy["professional_roles"]:
            job_roles_data.append({"role_id": int(role["id"])})
    # job_roles_data = [[{"role":36}],[{"role":36}],[],...]
    return job_roles_data


def build_job_skills_data(vacancy: dict) -> list:
    """prep job skills data for db

    Args:
        vacancy (dict): single job post

    Returns:
        list: [[{name: "SQL"},{name: "Python"}],...]
    """
    job_skills_data = []
    # job_skills_data = [[{name: "SQL"},{name: "Python"}],...]
    if vacancy["key_skills"] is not None and len(vacancy["key_skills"]) > 0:
        for skill in vacancy["key_skills"]:
            job_skills_data.append({"skill_name": skill["name"]})
    return job_skills_data


def split_vac_data(vacancies: list) -> None:
    """splits the data from the vacancies list into separate lists for each table
    Args:
        vacancies (list): list of job posts
    """
    jobs = []
    employers = []
    addresses = []
    languages = []
    salaries = []
    job_roles = []
    job_skills = []
    # Extracting and transforming data

    for vacancy in vacancies:

        job_data = build_job_data(vacancy)
        jobs.append(job_data)
        employer_data = build_employer_data(vacancy)
        employers.append(employer_data)
        address_data = build_address_data(vacancy)
        addresses.append(address_data)
        languages_data = build_languages_data(vacancy)
        languages.append(languages_data)
        salary_data = build_salaries_data(vacancy)
        print(salary_data)
        salaries.append(salary_data)
        job_roles_data = build_job_roles_data(vacancy)
        job_roles.append(job_roles_data)
        job_skills_data = build_job_skills_data(vacancy)
        job_skills.append(job_skills_data)

    return {
      "jobs":jobs,
      "employers": employers,
      "addresses": addresses,
      "salaries": salaries,
      "job_languages": languages,
      "job_roles": job_roles,
      "job_skills": job_skills
    }
