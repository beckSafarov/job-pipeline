from airflow.hooks.postgres_hook import PostgresHook #type:ignore


def get_db_engine():
    hook = PostgresHook(postgres_conn_id="supabase_db")  
    return hook.get_sqlalchemy_engine()
