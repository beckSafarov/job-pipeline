from airflow.hooks.postgres_hook import PostgresHook  # type:ignore
from sqlalchemy.orm import sessionmaker  # type:ignore
from sqlalchemy import select #type:ignore
from models.index import Job


def get_db_engine():
    hook = PostgresHook(postgres_conn_id="supabase_db")
    return hook.get_sqlalchemy_engine()


def create_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def query_latest_vacancy():
    session = create_session()
    query = (
        select(Job)  # Select all columns from Job table
        .order_by(Job.published_at.desc())  # Order by published_at DESC
        .limit(1)  # Limit to 1 row
    )
    return session.execute(query).scalar_one_or_none()
