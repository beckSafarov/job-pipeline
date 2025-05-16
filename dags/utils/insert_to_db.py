from models.index import Job,Employer,Address,Salary,JobLanguage,JobRole,JobSkill
from utils.db_utils import create_session
from sqlalchemy.dialects.postgresql import insert  # type:ignore
from data.data import model_pks


models_lookup = {
    "Employer": Employer,
    "Job":Job,
    "Address":Address,
    "Salary":Salary,
    "JobLanguage":JobLanguage,
    "JobRole":JobRole,
    "JobSkill":JobSkill,
}


def insert_new_job(data: list) -> list:
    source_ids = [item["source_id"] for item in data]
    session = create_session()
    # 1. Query existing jobs
    existing = (
        session.query(Job.source_id, Job.id).filter(Job.source_id.in_(source_ids)).all()
    )
    existing_map = {src_id: job_id for src_id, job_id in existing}

    inserted_ids = []

    for item in data:
        src_id = item["source_id"]

        # Skip if already exists
        if src_id in existing_map:
            inserted_ids.append(None)
            continue

        # Try inserting
        stmt = (
            insert(Job)
            .values(**item)
            .on_conflict_do_nothing(index_elements=["source_id"])
            .returning(Job.id)
        )
        result = session.execute(stmt)
        new_id = result.scalar()

        if new_id:
            inserted_ids.append(new_id)
            existing_map[src_id] = new_id  # optional: update the map

    session.commit()
    session.close()
    return inserted_ids


def insert_to_table(model_name: str, data: list) -> list | None:
    if data is None:
        print(f"No data for {model_name}")
        return []
    if len(data) < 1:
        return []

    if model_name == "Job":
        job_ids = insert_new_job(data)
        return job_ids
    print(f"Running {model_name}")
    session = create_session()
    model_class = models_lookup[model_name]

    try:
        # Process all items in a single transaction
        for item in data:
            stmt = (
                insert(model_class)
                .values(**item)
                .on_conflict_do_nothing(index_elements=model_pks[model_name])
                .returning(
                    model_class.id
                    if model_name in ["Job", "Employer"]
                    else model_class.job_id
                )
            )
            session.execute(stmt)

        # Flush and commit only once after processing all items
        session.flush()
        session.commit()
        return None

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
