from models.index import Job,Employer,Address,Salary,JobLanguage,JobRole,JobSkill
from sqlalchemy.orm import sessionmaker #type:ignore
from utils.get_db_engine import get_db_engine

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


def create_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def insert_to_table(model_name: str, data: list) -> list:
    if data is None:
        print(f"No data for {model_name}")
        return []
    if len(data) < 1:
        return []

    session = create_session()
    record_ids = []
    model_class = models_lookup[model_name]

    try:
        for item in data:
            if is_invalid_item(item):
                continue

            # Check if item already exists based on primary key
            # For tables with 'id' as primary key
            if "id" in item and item["id"] is not None:
                existing_record = (
                    session.query(model_class).filter_by(id=item["id"]).first()
                )
                if existing_record:
                    # Record already exists, skip insertion or update if needed
                    record_ids.append(existing_record.id)
                    continue
            # For tables with 'job_id' as primary key or part of composite key
            elif "job_id" in item:
                # Get primary key fields for this model
                primary_keys = [
                    key.name for key in model_class.__table__.primary_key.columns
                ]

                # Build filter conditions based on primary keys in the item
                filter_conditions = {}
                for pk in primary_keys:
                    if pk in item:
                        filter_conditions[pk] = item[pk]

                # Only check if we have all primary key values
                if len(filter_conditions) == len(primary_keys):
                    existing_record = (
                        session.query(model_class)
                        .filter_by(**filter_conditions)
                        .first()
                    )
                    if existing_record:
                        # For composite primary keys, we might not have a single .id field
                        # Still add job_id to record_ids if it exists
                        if hasattr(existing_record, "id"):
                            record_ids.append(existing_record.id)
                        elif hasattr(existing_record, "job_id"):
                            record_ids.append(existing_record.job_id)
                        continue

            # If we get here, record doesn't exist, so insert it
            record = model_class(**item)
            session.add(record)
            session.flush()  # Ensures record.id is generated

            # Add the ID to our return list
            if hasattr(record, "id"):
                record_ids.append(record.id)
            elif hasattr(record, "job_id"):
                record_ids.append(record.job_id)

        session.commit()
        return record_ids
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
