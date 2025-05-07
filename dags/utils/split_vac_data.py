import json 


def handle_work_format(formats: list)->str:
  if len(formats) < 1:
    return formats
  format_ids = [format['id'].lower() for format in formats]
  
  if 'on_site' in format_ids and 'remote' in format_ids:
    return 'hybrid'
  return format_ids[0]

def handle_work_hours(hours: list)->str:
    if len(hours) < 1:
      return hours
    elif len(hours) < 2:
      return hours[0]['id']
    elif all("HOURS" in s for s in hours):
      hours_numbers = [hour["id"].split("_")[1] for hour in hours]
      return max(hours_numbers)
    return hours[0]['id']

def split_vac_data(vacancies: list) -> None:
    jobs = []
    employers = []
    addresses = []
    languages = []
    salaries = []
    job_roles = []
    job_skills = []
    # Extracting and transforming data

    for vacancy in vacancies:
        job_data = {
            "source_id": int(vacancy["id"]),
            "title": vacancy["name"],
            "area_id": int(vacancy["area"]["id"]),
            "employer_id": int(vacancy["employer"]["id"]),
            "schedule": vacancy["schedule"]["id"],
            "work_format": handle_work_format(vacancy["work_format"]),
            "working_hours": handle_work_hours(vacancy["working_hours"]),
            "employment_form": vacancy["employment_form"]["id"],
            "experience": vacancy["experience"]['id'],
            "is_internship": vacancy["internship"],
            "description": vacancy["description"],
            "published_at": vacancy["published_at"],
        }
        jobs.append(job_data)

        employer_data = {
          "id": int(vacancy['employer']['id']),
          "name": vacancy['employer']['name'],
          "is_accredited": vacancy['employer']['accredited_it_employer'],
        }
        employers.append(employer_data)

        address_data = {}
        if vacancy['address'] is not None:
            address_data = {
              "lat": float(vacancy['address']['lat']),
              "lng": float(vacancy['address']['lng']),
              "city": vacancy['address']['city'],
              "street": vacancy['address']['street'],
              "building": vacancy['address']['building'],
            }
            addresses.append(address_data)

        languages_data = []
        if vacancy['languages'] is not None:
            for language in vacancy['languages']:
                languages_data.append({
                  "lang_id": language['id'],
                  "lang_level": language['level']['id'],
              })
        languages.append(languages_data)

        salary_data = {}
        if vacancy['salary'] is not None:
            salary_data = {
              "from": vacancy['salary']['from'],
              "to": vacancy['salary']['to'],
              "currency": vacancy['salary']['currency'],
          }
        salaries.append(salary_data)

        job_roles_data = []
        # job_roles_data = [[36],[36],[25]]
        # job_roles_data = [{role: 36}, {role: 25}, ...]
        if vacancy['professional_roles'] is not None:
            job_roles_data = {"role": vacancy["professional_roles"]["id"]}
            # job_roles_data = [int(role['id']) for role in vacancy['professional_roles']]
        job_roles.append(job_roles_data)

        job_skills_data = []
        # job_skills_data = [[{name: "SQL"},{name: "Python"}],...]
        if vacancy["key_skills"] is not None and len(vacancy["key_skills"]) > 0:
            job_skills_data = [skill['name'] for skill in vacancy['key_skills']]
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
