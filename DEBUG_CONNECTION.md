# Debugging SSL SYSCALL EOF Error

## Step 1: Check Your Supabase Connection String

1. Go to Airflow UI → Admin → Connections → `supabase_db`
2. Check which connection mode you're using:
   - **Transaction Mode** (port 6543) - PROBLEMATIC with SQLAlchemy
   - **Session Mode** (port 5432) - BETTER for this use case

### Fix: Use Session Mode or Direct Connection
Instead of: `[hostname]:6543/postgres`
Use: `[hostname]:5432/postgres` OR direct connection string

## Step 2: Add Connection Parameters

Add to your connection string or extra parameters:
```json
{
  "connect_timeout": 10,
  "keepalives": 1,
  "keepalives_idle": 30,
  "keepalives_interval": 10,
  "keepalives_count": 5,
  "tcp_user_timeout": 30000
}
```

## Step 3: Test Connection Stability

Run this test in a Python task:
```python
from utils.db_utils import create_session
import time

session = create_session()
for i in range(10):
    result = session.execute("SELECT 1").scalar()
    print(f"Test {i+1}: {result}")
    time.sleep(2)
session.close()
```

## Step 4: Check Supabase Dashboard

- Check connection count (might be hitting limits)
- Check if database is paused/restarting
- Check for any incidents

## Step 5: Enable SQLAlchemy Echo for Debugging

In `get_db_engine()`, add:
```python
engine = hook.get_sqlalchemy_engine()
engine.echo = True  # Shows all SQL
```

## Common Issues:

1. **Supabase Pooler in Transaction Mode**
   - Problem: PgBouncer closes connection after each transaction
   - Solution: Use Session Mode or disable pooler

2. **Connection Timeout**
   - Problem: Connection idle too long
   - Solution: Add keepalive settings

3. **SSL Issues**
   - Problem: SSL handshake failing
   - Solution: Add `sslmode=require` to connection string

4. **Supabase Project Paused**
   - Problem: Free tier projects pause after inactivity
   - Solution: Upgrade plan or handle pause/resume
