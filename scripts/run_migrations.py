import os
import sys
import re
import asyncio
import asyncpg

# Add core-app to sys.path to load settings
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "core-app"))
from config import settings

async def run_migrations():
    # Clean the connection string (asyncpg needs postgresql://, not postgresql+asyncpg://)
    db_url = settings.database_url.replace("+asyncpg", "")
    
    # Parse DB name from URL to check if it exists
    # e.g., postgresql://postgres:postgres@localhost:5432/autoresolve
    base_url, db_name = db_url.rsplit("/", 1)
    # Strip any query parameters from db_name if present
    db_name = db_name.split("?")[0]
    
    print(f"Checking if database '{db_name}' exists...")
    try:
        admin_conn = await asyncpg.connect(f"{base_url}/postgres")
        try:
            exists = await admin_conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1;", db_name)
            if not exists:
                print(f"Database '{db_name}' does not exist. Creating...")
                await admin_conn.execute(f'CREATE DATABASE "{db_name}";')
                print(f"Database '{db_name}' created successfully.")
            else:
                print(f"Database '{db_name}' exists.")
        finally:
            await admin_conn.close()
    except Exception as e:
        print(f"Warning: Could not check/create database using admin connection: {e}")
        print("Will attempt direct connection...")

    print(f"Connecting to database '{db_name}' to run migrations...")
    conn = await asyncpg.connect(db_url)
    try:
        # Create migration tracking table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Retrieve already applied migrations
        rows = await conn.fetch("SELECT version FROM schema_migrations;")
        applied = {r["version"] for r in rows}
        
        # Read migration files
        migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "migrations"))
        if not os.path.exists(migrations_dir):
            print(f"Migrations directory not found at {migrations_dir}", file=sys.stderr)
            sys.exit(1)
            
        files = [f for f in os.listdir(migrations_dir) if f.endswith(".sql") and f.startswith("V")]
        
        # Sort by version number (e.g. V1, V2, V10 etc.)
        def extract_version(filename):
            match = re.match(r"^V(\d+)", filename)
            return int(match.group(1)) if match else 0
            
        files.sort(key=extract_version)
        
        for file in files:
            if file in applied:
                print(f"Skipping applied migration: {file}")
                continue
                
            print(f"Applying migration {file}...")
            filepath = os.path.join(migrations_dir, file)
            with open(filepath, "r", encoding="utf-8") as f:
                sql = f.read()
                
            # Run in transaction
            async with conn.transaction():
                # asyncpg's conn.execute runs multi-statement scripts
                await conn.execute(sql)
                await conn.execute("INSERT INTO schema_migrations (version) VALUES ($1);", file)
            print(f"Successfully applied migration {file}")
            
        print("All migrations checked and up-to-date.")
    except Exception as e:
        print(f"Error during migration execution: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migrations())
