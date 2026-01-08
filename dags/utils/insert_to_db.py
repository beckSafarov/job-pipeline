from models.index import (
    Job,
    Employer,
    Address,
    Salary,
    JobLanguage,
    JobRole,
    JobSkill,
    JobProcessed,
)
from utils.db_utils import create_session, execute_with_retry
from sqlalchemy.dialects.postgresql import insert  # type:ignore
from sqlalchemy.exc import OperationalError  # type:ignore
from data.data import model_pks
import time


models_lookup = {
    "Employer": Employer,
    "JobProcessed": JobProcessed,
    "Job": Job,
    "Address": Address,
    "Salary": Salary,
    "JobLanguage": JobLanguage,
    "JobRole": JobRole,
    "JobSkill": JobSkill,
}


def insert_new_job(data: list) -> list:
    source_ids = [item["source_id"] for item in data]
    session = create_session()

    # 1. Query existing jobs first
    existing = (
        session.query(Job.source_id, Job.id).filter(Job.source_id.in_(source_ids)).all()
    )
    existing_map = {src_id: job_id for src_id, job_id in existing}

    inserted_ids = []
    for item in data:
        src_id = item["source_id"]

        # If job already exists, use existing ID
        if src_id in existing_map:
            inserted_ids.append(existing_map[src_id])
            continue

        try:
            # Try inserting new job
            stmt = (
                insert(Job)
                .values(**item)
                .on_conflict_do_nothing(index_elements=["source_id"])
                .returning(Job.id)
            )
            result = session.execute(stmt)
            new_id = result.scalar()
            # print(f"new id:")
            # print(new_id)
            if new_id:
                inserted_ids.append(new_id)
                existing_map[src_id] = new_id  # Update the map for consistency
        except Exception as e:
            session.rollback()
            print(f"Insert failed: {e}")

    # print("Inserted ids:")
    # print(inserted_ids)
    session.commit()
    session.close()
    return inserted_ids


def insert_to_table(model_name: str, data: list) -> list | None:
    if data is None:
        return []
    if len(data) < 1:
        return []
    if model_name == "Job":
        job_ids = insert_new_job(data)
        return job_ids

    print(f"Running {model_name} - inserting {len(data)} records")

    # Process in batches to avoid connection timeouts
    batch_size = 50  # Reduced from 100 for more frequent commits
    total_batches = (len(data) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(data))
        batch_data = data[start_idx:end_idx]

        print(
            f"  Processing batch {batch_num + 1}/{total_batches} ({len(batch_data)} records)"
        )

        # Use the retry wrapper
        def process_batch(session):
            model_class = models_lookup[model_name]

            for item in batch_data:
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

            session.commit()
            return True

        try:
            execute_with_retry(process_batch, max_retries=5, initial_wait=2)
            print(f"  ✓ Batch {batch_num + 1} committed successfully")
        except Exception as e:
            print(f"  ❌ Failed to insert batch {batch_num + 1} after all retries: {e}")
            raise

    print(f"✅ {model_name} insertion complete")
    return None
