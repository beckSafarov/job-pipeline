from airflow.providers.postgres.hooks.postgres import PostgresHook  # type:ignore
from sqlalchemy.orm import sessionmaker  # type:ignore
from sqlalchemy import select  # type:ignore
import json

def get_db_engine():
    hook = PostgresHook(postgres_conn_id="supabase_db")
    return hook.get_sqlalchemy_engine()


def create_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


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
