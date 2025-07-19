from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/postgres"

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("✅ Connected to database.")

    # Use text() for raw SQL in SQLAlchemy 2.0+
    result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
    tables = [row[0] for row in result]
    
    print("✅ Tables in public schema:")
    for table in tables:
        print("-", table)
    
    connection.close()
except OperationalError as e:
    print("❌ Error connecting to database:", e)
