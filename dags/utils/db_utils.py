from airflow.providers.postgres.hooks.postgres import PostgresHook  # type:ignore
from sqlalchemy.orm import sessionmaker, noload  # type:ignore
from sqlalchemy import select, extract, event  # type:ignore
from sqlalchemy.pool import Pool  # type:ignore
from sqlalchemy.exc import OperationalError  # type:ignore
import json
from decimal import Decimal
from datetime import datetime
import time

def get_db_engine():
    hook = PostgresHook(postgres_conn_id="supabase_db")

    # Get engine with proper connection arguments
    connect_args = {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }

    engine = hook.get_sqlalchemy_engine()

    # Configure connection pool for better stability
    engine.pool._max_overflow = 10
    engine.pool._pool_size = 5

    # Set connection pool recycle time to prevent stale connections (10 minutes)
    # Reduced from 25 min to be more aggressive
    engine.pool._recycle = 600

    # Enable pre-ping to check connection health before using
    engine.pool._pre_ping = True

    return engine


def create_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def execute_with_retry(func, max_retries=3, initial_wait=1):
    """
    Execute a database function with automatic retry on connection errors.

    Args:
        func: A function that takes a session as argument and performs DB operations
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds (doubles with each retry)

    Returns:
        Result from the function

    Example:
        def my_insert(session):
            session.execute(stmt)
            session.commit()

        execute_with_retry(my_insert)
    """
    last_error = None

    for attempt in range(max_retries):
        session = create_session()
        try:
            result = func(session)
            session.close()
            return result

        except OperationalError as e:
            session.rollback()
            session.close()
            last_error = e

            error_str = str(e)
            is_connection_error = any(
                keyword in error_str.lower()
                for keyword in ["ssl", "eof", "connection", "timeout", "broken pipe"]
            )

            if is_connection_error and attempt < max_retries - 1:
                wait_time = initial_wait * (2**attempt)
                print(f"⚠️ Connection error (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"⏳ Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise

        except Exception as e:
            session.rollback()
            session.close()
            raise

    # If we get here, all retries failed
    raise last_error


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
    query = select(Job).order_by(Job.published_at.desc()).limit(1)
    result = session.execute(query).scalar_one_or_none()
    if result is None:
        json_data = {}  # Or None, depending on your needs
    else:
        # Convert model instance to dictionary
        json_data = {
            column.name: getattr(result, column.name)
            for column in result.__table__.columns
        }

    # Serialize to JSON
    json_string = json.dumps(json_data, default=str)
    # file_path = "/tmp/latest_vacancy.json"
    # write_json(json_data, file_path)
    return json_data


def query_latest_vacancy_to_update():
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
