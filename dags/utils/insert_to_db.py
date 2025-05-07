from models.index import Job,Employer,Address,Salary,JobLanguage,JobRole,JobSkill
from sqlalchemy.orm import sessionmaker #type:ignore
from utils.get_db_engine import get_db_engine

def map_ids_to_values(ids: list, data:list)->list:
    map_dict = []
    for i, id in enumerate(ids):
        map_dict.append({
            "job_id":id,
            "role_id":data[i]
        })
    return map_dict


models_lookup = {
    "Employer": Employer,
    "Job":Job,
    "Address":Address,
    "Salary":Salary,
    "JobLanguage":JobLanguage,
    "JobRole":JobRole,
    "JobSkill":JobSkill,
}

def is_invalid_item(item):
    return type(item) is not dict or len(list(item.keys())) < 1

def insert_to_table(model_name:str, data: list)->list:
    if len(data) < 1:
        return []
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    record_ids = []
    model_class = models_lookup[model_name]

    try:
        for item in data:
            if is_invalid_item(item):
                continue
            record = model_class(**item)
            session.add(record)
            session.flush()  # Ensures record.id is generated
            record_ids.append(record.id)

        session.commit()
        return record_ids

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

def insert_employers(employers_data: list)->list:
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    employer_ids = []

    try:
        for emp_dict in employers_data:
            employer = Employer(**emp_dict)
            session.add(employer)
            session.flush()  # Ensures employer.id is generated
            employer_ids.append(employer.id)

        session.commit()
        return employer_ids

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

def insert_jobs(jobs_data: list)->list:
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    job_ids = []

    try:
        for job_dict in jobs_data:
            job = Job(**job_dict)
            session.add(job)
            session.flush()  # Ensures job.id is generated
            job_ids.append(job.id)

        session.commit()
        return job_ids

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()
