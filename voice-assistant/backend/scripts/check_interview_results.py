import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
    sys.exit(1)

try:
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Execute raw SQL to count records
    result = db.execute(text("""
        SELECT 
            COUNT(*) as total_count,
            COUNT(DISTINCT session_id) as distinct_sessions,
            MIN(created_at) as first_created,
            MAX(created_at) as last_created
        FROM interview_results
    """))
    
    stats = result.fetchone()
    print("\n=== Database Statistics ===")
    print(f"Total records: {stats[0]}")
    print(f"Distinct session IDs: {stats[1]}")
    print(f"First record created at: {stats[2]}")
    print(f"Last record created at: {stats[3]}")
    
    # Get all records with session_id and timestamps
    records = db.execute(text("""
        SELECT 
            id,
            session_id,
            user_id,
            created_at,
            updated_at
        FROM interview_results
        ORDER BY created_at DESC
    """))
    
    print("\n=== All Interview Results ===")
    for idx, row in enumerate(records, 1):
        print(f"\n{idx}. ID: {row[0]}")
        print(f"   Session ID: {row[1]}")
        print(f"   User ID: {row[2]}")
        print(f"   Created: {row[3]}")
        print(f"   Updated: {row[4]}")
    
    # Check for duplicate session_ids
    duplicates = db.execute(text("""
        SELECT 
            session_id,
            COUNT(*) as count
        FROM interview_results
        GROUP BY session_id
        HAVING COUNT(*) > 1
    """))
    
    dup_count = 0
    print("\n=== Duplicate Session IDs ===")
    for dup in duplicates:
        dup_count += 1
        print(f"Session ID: {dup[0]} appears {dup[1]} times")
    
    if dup_count == 0:
        print("No duplicate session IDs found")
    
    db.close()
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
