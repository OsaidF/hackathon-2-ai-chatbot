#!/usr/bin/env python3
"""
Migration runner script for Todo AI Chatbot database migrations.

This script executes SQL migration files in order to set up or update the database schema.

Usage:
    python -m migrations.run

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (required)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()


def get_database_url():
    """Get database URL from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def parse_database_url(url):
    """
    Parse PostgreSQL database URL into components.

    Args:
        url: PostgreSQL connection URL

    Returns:
        dict: Database connection parameters
    """
    # Remove postgresql:// or postgresql+asyncpg:// prefix
    clean_url = url.replace("postgresql+asyncpg://", "").replace("postgresql://", "")

    # Parse connection string
    # Format: user:password@host:port/database
    if "@" in clean_url:
        auth_part, rest = clean_url.split("@")
        user_password = auth_part.split(":")
        user = user_password[0]
        password = user_password[1] if len(user_password) > 1 else ""

        # Split host:port/database
        if "/" in rest:
            host_port, database = rest.split("/")
            host = host_port.split(":")[0]
            port = int(host_port.split(":")[1]) if ":" in host_port else 5432
        else:
            host = rest
            port = 5432
            database = "postgres"
    else:
        raise ValueError(f"Invalid database URL format: {url}")

    # Extract SSL parameters
    ssl_mode = "require"
    if "?" in database:
        database, params = database.split("?")
        if "sslmode=" in params:
            ssl_mode = params.split("sslmode=")[1].split("&")[0]

    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": database,
        "sslmode": ssl_mode
    }


def run_migration_file(connection, migration_file):
    """
    Execute a single migration file.

    Args:
        connection: psycopg2 database connection
        migration_file: Path to migration SQL file

    Returns:
        bool: True if migration succeeded, False otherwise
    """
    print(f"Running migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    try:
        # Execute migration SQL
        with connection.cursor() as cursor:
            cursor.execute(migration_sql)

        connection.commit()
        print(f"✓ Migration {migration_file.name} completed successfully")
        return True

    except Exception as e:
        connection.rollback()
        print(f"✗ Migration {migration_file.name} failed: {str(e)}")
        return False


def main():
    """Main migration runner."""
    try:
        # Get database connection parameters
        database_url = get_database_url()
        db_params = parse_database_url(database_url)

        print(f"Connecting to database: {db_params['host']}:{db_params['port']}/{db_params['database']}")

        # Connect to PostgreSQL
        connection = psycopg2.connect(**db_params)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        print("✓ Database connection established")

        # Get migration files directory
        migrations_dir = Path(__file__).parent
        if not migrations_dir.exists():
            print(f"✗ Migrations directory not found: {migrations_dir}")
            sys.exit(1)

        # Get all migration files sorted by name
        migration_files = sorted(
            migrations_dir.glob("*.sql"),
            key=lambda x: x.name
        )

        if not migration_files:
            print("No migration files found")
            sys.exit(0)

        print(f"Found {len(migration_files)} migration file(s)")

        # Run each migration file
        success_count = 0
        for migration_file in migration_files:
            if run_migration_file(connection, migration_file):
                success_count += 1
            else:
                print(f"\n⚠️  Migration failed. Stopping.")
                connection.close()
                sys.exit(1)

        connection.close()

        print(f"\n✓ All {success_count} migration(s) completed successfully!")
        sys.exit(0)

    except ValueError as e:
        print(f"✗ Configuration error: {str(e)}")
        sys.exit(1)

    except psycopg2.OperationalError as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify DATABASE_URL is correct in .env file")
        print("2. Ensure PostgreSQL database is running")
        print("3. Check network connectivity to database host")
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
