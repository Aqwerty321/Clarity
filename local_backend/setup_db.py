"""
Database setup script
Creates the PostgreSQL database and initializes tables
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import psycopg

def create_database():
    """Create the clarity_db database if it doesn't exist"""
    # Parse DATABASE_URL to get connection params
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/clarity_db")
    
    # Extract components
    # Format: postgresql+psycopg://user:password@host:port/dbname
    parts = db_url.replace("postgresql+psycopg://", "").replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_port_db = parts[1].split("/")
    host_port = host_port_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    dbname = host_port_db[1]
    
    print(f"🔌 Connecting to PostgreSQL at {host}:{port}")
    
    try:
        # Connect to PostgreSQL (default postgres database)
        conn = psycopg.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📦 Creating database '{dbname}'...")
            cursor.execute(f'CREATE DATABASE {dbname}')
            print(f"✅ Database '{dbname}' created successfully!")
        else:
            print(f"✅ Database '{dbname}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("\n⚠️  Make sure PostgreSQL is installed and running!")
        print("   Install PostgreSQL: https://www.postgresql.org/download/")
        print("   Or use Docker: docker run --name clarity-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres")
        return False
    
    return True


def init_tables():
    """Initialize database tables using SQLAlchemy"""
    print("\n📋 Initializing database tables...")
    
    try:
        from app.db import init_db
        init_db()
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("🗄️  Clarity Database Setup")
    print("=" * 60)
    print()
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    if not init_tables():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ Database setup complete!")
    print("=" * 60)
    print()
    print("📝 Connection details:")
    print(f"   DATABASE_URL: {os.getenv('DATABASE_URL')}")
    print()
    print("🚀 You can now start the backend:")
    print("   cd local_backend")
    print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5000")
    print()


if __name__ == "__main__":
    main()
