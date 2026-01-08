"""
Temporary DAG to test Supabase connection stability.
Run this to diagnose connection issues.
"""
from airflow.decorators import dag, task
from pendulum import datetime
import time

@dag(
    start_date=datetime(2025, 1, 1),
    schedule=None,  # Manual trigger only
    catchup=False,
    tags=["debug", "connection-test"],
)
def test_supabase_connection():
    
    @task
    def test_connection_stability():
        """Test if connection stays alive during operations."""
        from utils.db_utils import create_session
        
        print("🔍 Testing Supabase connection stability...")
        
        for i in range(10):
            try:
                session = create_session()
                result = session.execute("SELECT 1 as test").scalar()
                session.close()
                print(f"✓ Test {i+1}/10: Connection OK (result={result})")
                time.sleep(2)  # Wait 2 seconds between tests
            except Exception as e:
                print(f"❌ Test {i+1}/10 FAILED: {e}")
                raise
        
        print("✅ All connection tests passed!")
    
    @task
    def test_insert_with_delay():
        """Test if insert works after a delay."""
        from utils.db_utils import create_session, execute_with_retry
        from models.index import Employer
        from sqlalchemy.dialects.postgresql import insert
        
        print("🔍 Testing insert with connection delay...")
        
        def do_insert(session):
            # Test employer data
            test_data = {
                "id": -999999,  # Negative to avoid conflicts
                "name": "TEST_CONNECTION_EMPLOYER",
                "is_accredited": False
            }
            
            stmt = (
                insert(Employer)
                .values(**test_data)
                .on_conflict_do_nothing(index_elements=["id"])
            )
            session.execute(stmt)
            session.commit()
            print("✓ Insert successful")
        
        # Wait 30 seconds to simulate delay
        print("⏳ Waiting 30 seconds before insert...")
        time.sleep(30)
        
        try:
            execute_with_retry(do_insert)
            print("✅ Insert after delay succeeded!")
        except Exception as e:
            print(f"❌ Insert after delay failed: {e}")
            raise
    
    @task
    def check_connection_info():
        """Display connection information."""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        hook = PostgresHook(postgres_conn_id="supabase_db")
        conn = hook.get_connection("supabase_db")
        
        print("📊 Connection Information:")
        print(f"  Host: {conn.host}")
        print(f"  Port: {conn.port}")
        print(f"  Database: {conn.schema}")
        print(f"  Login: {conn.login}")
        print(f"  Extra: {conn.extra}")
        
        # Check if using transaction mode (problematic)
        if conn.port == 6543:
            print("⚠️ WARNING: Using Transaction Mode (port 6543)")
            print("   This can cause 'SSL SYSCALL error: EOF' issues")
            print("   Recommend: Switch to Session Mode (port 5432)")
        else:
            print("✓ Not using Transaction Mode")
    
    info = check_connection_info()
    stability = test_connection_stability()
    insert_test = test_insert_with_delay()
    
    info >> stability >> insert_test

# Instantiate
test_supabase_connection()
