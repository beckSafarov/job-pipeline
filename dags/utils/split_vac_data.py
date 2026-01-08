from utils.currency_utils import convert_to_usd

import re  # for regex operations
import hashlib  # for generating synthetic IDs


def clean_description(text: str) -> str:
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Collapse multiple spaces into one
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def handle_work_format(formats: list) -> str:
    if len(formats) < 1:
        return formats

    # Defensive check for missing 'id' key
    format_ids = []
    for fmt in formats:
        if isinstance(fmt, dict) and "id" in fmt:
            format_ids.append(fmt["id"].lower())
        else:
            print(f"⚠️ WARNING: work_format item missing 'id' key: {fmt}")

    if not format_ids:
        return ""

    if "on_site" in format_ids and "remote" in format_ids:
        return "hybrid"
    return format_ids[0]


def handle_work_hours(hours: list)->str:
    if len(hours) < 1:
        return hours

    # Defensive check for missing 'id' key
    if len(hours) < 2:
        if isinstance(hours[0], dict) and "id" in hours[0]:
            return hours[0]["id"]
        else:
            print(f"⚠️ WARNING: working_hours item missing 'id' key: {hours[0]}")
            return ""

    # Check if all items have 'id' key before processing
    valid_hours = [h for h in hours if isinstance(h, dict) and "id" in h]
    if not valid_hours:
        print(f"⚠️ WARNING: No valid working_hours items with 'id' key")
        return ""

    if all("HOURS" in h.get("id", "") for h in valid_hours):
        hours_numbers = [hour["id"].split("_")[1] for hour in valid_hours]
        return max(hours_numbers)

    return valid_hours[0]["id"]


def build_job_data(vacancy: dict) -> dict:
    """Build job data with defensive checks for nested fields."""

    # Helper function to safely get nested ID
    def safe_get_id(obj, field_name, default=None):
        if obj is None:
            print(
                f"⚠️ WARNING: '{field_name}' is None in vacancy {vacancy.get('id', 'UNKNOWN')}"
            )
            return default
        if not isinstance(obj, dict):
            print(
                f"⚠️ WARNING: '{field_name}' is not a dict in vacancy {vacancy.get('id', 'UNKNOWN')}: {type(obj)}"
            )
            return default
        if "id" not in obj:
            print(
                f"❌ ERROR: '{field_name}' missing 'id' key in vacancy {vacancy.get('id', 'UNKNOWN')}"
            )
            print(f"   Available keys in {field_name}: {list(obj.keys())}")
            print(f"   {field_name} data: {obj}")
            return default
        return obj["id"]

    # Special handling for employer to generate synthetic ID if needed
    def get_employer_id(employer_obj):
        if employer_obj is None:
            return 0
        if not isinstance(employer_obj, dict):
            return 0
        if "id" in employer_obj:
            return int(employer_obj["id"])
        # Generate synthetic ID from name
        employer_name = employer_obj.get("name", "Unknown")
        synthetic_id = generate_employer_id(employer_name)
        print(
            f"⚠️ WARNING: Employer in vacancy {vacancy.get('id', 'UNKNOWN')} missing 'id'. Generated synthetic ID {synthetic_id}"
        )
        return synthetic_id

    try:
        return {
            "source_id": int(vacancy["id"]),
            "title": vacancy["name"],
            "area_id": int(safe_get_id(vacancy.get("area"), "area", 0)),
            "employer": get_employer_id(vacancy.get("employer")),
            "schedule": safe_get_id(vacancy.get("schedule"), "schedule", ""),
            "work_format": handle_work_format(vacancy.get("work_format", [])),
            "working_hours": handle_work_hours(vacancy.get("working_hours", [])),
            "employment_form": safe_get_id(
                vacancy.get("employment_form"), "employment_form", ""
            ),
            "experience": safe_get_id(vacancy.get("experience"), "experience", ""),
            "is_internship": vacancy.get("internship", False),
            "description": vacancy.get("description", ""),
            "published_at": vacancy["published_at"],
        }
    except KeyError as e:
        print(
            f"❌ CRITICAL ERROR in build_job_data for vacancy {vacancy.get('id', 'UNKNOWN')}"
        )
        print(f"   Missing key: {e}")
        print(f"   Vacancy keys: {list(vacancy.keys())}")
        raise


def generate_employer_id(employer_name: str) -> int:
    """
    Generate a deterministic employer ID from the employer name.
    Uses hash to ensure the same name always produces the same ID.
    Uses negative numbers to distinguish from real HH employer IDs.
    """
    # Create a hash of the employer name
    hash_object = hashlib.md5(employer_name.encode())
    # Convert to integer and make it negative to distinguish from real IDs
    # Use modulo to keep it within reasonable integer range
    synthetic_id = -(int(hash_object.hexdigest(), 16) % 1000000000)
    return synthetic_id


def build_employer_data(vacancy: dict) -> dict:
    if "employer" not in vacancy or vacancy["employer"] is None:
        return {}

    employer = vacancy["employer"]

    # Check if employer has an ID
    if "id" in employer:
        employer_id = int(employer["id"])
    else:
        # Generate synthetic ID from name
        employer_name = employer.get("name", "Unknown")
        employer_id = generate_employer_id(employer_name)
        print(
            f"⚠️ WARNING: Employer missing 'id'. Generated synthetic ID {employer_id} for '{employer_name}'"
        )

    return {
        "id": employer_id,
        "name": employer.get("name", "Unknown"),
        "is_accredited": employer.get("accredited_it_employer", False),
    }


def build_address_data(vacancy: dict) -> dict:
    # Handle both API data (with nested address) and database data (flat structure)
    if "address" in vacancy and vacancy["address"] is not None:
        # API data structure
        return {
            "lat": float(vacancy["address"]["lat"]),
            "lng": float(vacancy["address"]["lng"]),
            "city": vacancy["address"]["city"],
            "street": vacancy["address"]["street"],
            "building": vacancy["address"]["building"],
        }
    else:
        # Database data structure or no address data
        return {}


def build_languages_data(vacancy: dict) -> list:
    # Handle both API data (with nested languages) and database data (flat structure)
    if "languages" in vacancy and vacancy["languages"] is not None:
        # API data structure
        languages_data = []
        for language in vacancy["languages"]:
            languages_data.append(
                {
                    "lang_id": language["id"],
                    "lang_level": language["level"]["id"],
                }
            )
        return languages_data
    else:
        # Database data structure or no languages data
        return []


def build_salaries_data(vacancy: dict) -> dict:
    # Handle both API data (with nested salary) and database data (flat structure)

    def get_usd_value(amount, currency):
        if amount is None or currency is None:
            return None
        return convert_to_usd(amount, currency)

    if "salary" in vacancy and vacancy["salary"] is not None:
        # API data structure
        salary_data = {
            "salary_from": vacancy["salary"]["from"],
            "salary_to": vacancy["salary"]["to"],
            "currency": vacancy["salary"]["currency"],
            "salary_from_usd": get_usd_value(
                vacancy["salary"]["from"], vacancy["salary"]["currency"]
            ),
            "salary_to_usd": get_usd_value(
                vacancy["salary"]["to"], vacancy["salary"]["currency"]
            ),
        }
        return salary_data
    else:
        # Database data structure or no salary data
        return {}


def build_job_roles_data(vacancy: dict) -> list:
    # Handle both API data (with nested professional_roles) and database data (flat structure)
    job_roles_data = []
    if "professional_roles" in vacancy and vacancy["professional_roles"] is not None:
        # API data structure
        for role in vacancy["professional_roles"]:
            job_roles_data.append({"role_id": int(role["id"])})
    # For database data, we don't have this nested structure, so return empty list
    return job_roles_data


def build_job_skills_data(vacancy: dict) -> list:
    """prep job skills data for db

    Args:
        vacancy (dict): single job post

    Returns:
        list: [[{name: "SQL"},{name: "Python"}],...]
    """
    job_skills_data = []
    # Handle both API data (with nested key_skills) and database data (flat structure)
    if (
        "key_skills" in vacancy
        and vacancy["key_skills"] is not None
        and len(vacancy["key_skills"]) > 0
    ):
        # API data structure
        for skill in vacancy["key_skills"]:
            job_skills_data.append({"skill_name": skill["name"]})
    # For database data, we don't have this nested structure, so return empty list
    return job_skills_data


def build_job_processed(vacancy: dict) -> list:
    def get_pro_role(vacancy: dict) -> str:
        if "professional_roles" in vacancy and vacancy["professional_roles"]:
            return vacancy["professional_roles"][0]["id"]
        return None

    return {
        "description": clean_description(vacancy.get("description", "")),
        "role_id": get_pro_role(vacancy),
    }


def split_vac_data(vacancies: list) -> None:
    """splits the data from the vacancies list into separate lists for each table
    Args:
        vacancies (list): list of job posts
    """
    jobs = []
    jobs_processed = []
    employers = []
    addresses = []
    languages = []
    salaries = []
    job_roles = []
    job_skills = []
    # Extracting and transforming data

    for i, vacancy in enumerate(vacancies):
        try:
            print(
                f"🔄 Processing vacancy {i+1}/{len(vacancies)}: ID={vacancy.get('id', 'UNKNOWN')}"
            )
            job_data = build_job_data(vacancy)
            jobs.append(job_data)
            job_processed = build_job_processed(vacancy)
            jobs_processed.append(job_processed)
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
        except Exception as e:
            print(
                f"❌ ERROR processing vacancy {i+1} (ID={vacancy.get('id', 'UNKNOWN')}): {e}"
            )
            print(f"   Vacancy data: {vacancy}")
            raise

    return {
        "jobs": jobs,
        "jobs_processed": jobs_processed,
        "employers": employers,
        "addresses": addresses,
        "salaries": salaries,
        "job_languages": languages,
        "job_roles": job_roles,
        "job_skills": job_skills,
    }
