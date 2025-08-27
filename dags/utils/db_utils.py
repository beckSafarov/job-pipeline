from airflow.providers.postgres.hooks.postgres import PostgresHook  # type:ignore
from sqlalchemy.orm import sessionmaker, noload  # type:ignore
from sqlalchemy import select, extract  # type:ignore
import json
from decimal import Decimal
from datetime import datetime

def get_db_engine():
    hook = PostgresHook(postgres_conn_id="supabase_db")
    return hook.get_sqlalchemy_engine()


def create_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def convert_to_serializable(obj):
    """Convert non-JSON serializable objects to serializable types."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif obj is None:
        return None
    else:
        # For any other type, try to return as-is
        # This should handle basic types like int, str, bool, float
        return obj


def serialize_job_to_dict(job):
    """
    Safely serialize a SQLAlchemy Job object to a dictionary,
    avoiding relationship loading issues.
    """
    job_dict = {}

    # Explicitly get each column value without triggering relationships
    for column in job.__table__.columns:
        try:
            # Get the raw column value without accessing relationships
            raw_value = getattr(job, column.name)
            job_dict[column.name] = convert_to_serializable(raw_value)
        except Exception as e:
            print(f"Error serializing column {column.name}: {e}")
            job_dict[column.name] = None

    return job_dict


def query_latest_vacancy():
    from models.index import Job

    session = create_session()

    try:
        # Use noload() to prevent loading relationships
        query = (
            select(Job)
            .options(
                noload(Job.area),
                noload(Job.employer),
                noload(Job.address),
                noload(Job.languages),
                noload(Job.skills),
                noload(Job.roles),
                noload(Job.salary),
            )
            .order_by(Job.published_at.desc())
            .limit(1)
        )

        result = session.execute(query).scalar_one_or_none()

        if result is None:
            json_data = {}  # Or None, depending on your needs
        else:
            # Use the safe serializer
            json_data = serialize_job_to_dict(result)

        return json_data

    except Exception as e:
        print(f"Error querying latest vacancy: {e}")
        return {}

    finally:
        session.close()


def query_jobs_published_in_month(month=None, year=None):
    """
    Retrieve all jobs from the database that were published in a specific month and/or year.

    Args:
        month (int, optional): The month to filter by (1-12). If not provided,
                              returns jobs from all months.
        year (int, optional): The year to filter by. If not provided,
                             returns jobs from all years.

    Returns:
        list: A list of dictionaries containing job data published in the specified period.
    """
    from models.index import Job

    session = create_session()

    try:
        # Build the base query
        # Use noload() to prevent loading any relationships
        query = select(Job).options(
            noload(Job.area),
            noload(Job.employer),
            noload(Job.address),
            noload(Job.languages),
            noload(Job.skills),
            noload(Job.roles),
            noload(Job.salary),
        )

        # Add month filter if specified
        if month:
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
            query = query.where(extract("month", Job.published_at) == month)

        # Add year filter if specified
        if year:
            query = query.where(extract("year", Job.published_at) == year)

        # Order by published_at descending to get most recent first
        query = query.order_by(Job.published_at.desc())

        results = session.execute(query).scalars().all()

        # Convert model instances to dictionaries using the safe serializer
        jobs_data = []
        for job in results:
            job_dict = serialize_job_to_dict(job)
            jobs_data.append(job_dict)

        return jobs_data

    except Exception as e:
        print(f"Error querying jobs published in specified period: {e}")
        return []

    finally:
        session.close()


def query_jobs_published_in_june(year=None):
    """
    Retrieve all jobs from the database that were published in June.
    This is a convenience wrapper around query_jobs_published_in_month.

    Args:
        year (int, optional): The year to filter by. If not provided,
                             returns jobs from June of any year.

    Returns:
        list: A list of dictionaries containing job data published in June.
    """
    return query_jobs_published_in_month(month=6, year=year)
