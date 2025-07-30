#!/usr/bin/env python3
"""
Supabase Migration Tool
-----------------------
This script migrates data from a cloud Supabase instance to a local Supabase instance.
It automatically discovers all tables in the source database and migrates their data.
"""
from supabase import create_client, Client
from time import sleep
from typing import List, Optional
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# === 1. Configuration ===

# Cloud Supabase (source)
CLOUD_URL = os.getenv("SUPABASE_CLOUD_URL", "https://your-cloud-project.supabase.co")
CLOUD_KEY = os.getenv("SUPABASE_CLOUD_KEY", "your-cloud-service-role-key")

# Local Supabase (target)
LOCAL_URL = os.getenv("SUPABASE_LOCAL_URL", "http://localhost:54321")
LOCAL_KEY = os.getenv("SUPABASE_LOCAL_KEY", "your-local-service-role-key")

# Exclude system tables and auth tables by default
EXCLUDE_PATTERNS = [
    '^pg_',  # PostgreSQL system tables
    '^sql_',  # System tables
    '^_',     # Tables starting with underscore
    '^storage',  # Storage tables
    '^realtime',  # Realtime tables
    '^supabase',  # Supabase system tables
    '^auth',      # Auth tables
    '^extensions' # Extensions
]

# Optional: Only include specific schemas (public by default)
INCLUDE_SCHEMAS = ['public']  # Add other schemas if needed

# === 2. Create clients ===

def create_supabase_clients() -> tuple[Client, Client]:
    """Create and return Supabase client instances."""
    try:
        supabase_cloud = create_client(CLOUD_URL, CLOUD_KEY)
        supabase_local = create_client(LOCAL_URL, LOCAL_KEY)
        return supabase_cloud, supabase_local
    except Exception as e:
        print(f"❌ Error creating Supabase clients: {e}")
        raise

# === 3. Migration process ===

def migrate_table(supabase_cloud: Client, supabase_local: Client, table: str) -> int:
    """Migrate data for a single table."""
    print(f"\n🔄 Migrating table: {table}")
    start = 0
    page_size = 1000
    total_inserted = 0

    while True:
        try:
            # Fetch a page of data from cloud
            response = (
                supabase_cloud.table(table)
                .select("*")
                .range(start, start + page_size - 1)
                .execute()
            )
            rows = response.data

            if not rows:
                break

            # Insert rows into local
            for row in rows:
                try:
                    supabase_local.table(table).insert(row).execute()
                    total_inserted += 1
                except Exception as e:
                    print(f"⚠️ Error inserting row into {table}: {e}")
                    continue

            print(f"- Copied {len(rows)} records (total: {total_inserted})")
            start += page_size

            # Small delay to avoid rate limiting
            sleep(0.1)

        except Exception as e:
            print(f"❌ Error during migration of {table}: {e}")
            break

    return total_inserted

def get_tables(supabase: Client) -> List[str]:
    """Fetch all tables from the Supabase instance."""
    try:
        # Get all tables from information_schema
        query = """
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema = ANY(%s)
        """
        
        # Execute raw query to get all tables
        response = supabase.rpc('pg_query', {'query': query, 'params': [INCLUDE_SCHEMAS]}).execute()
        
        if not hasattr(response, 'data') or not response.data:
            print("⚠️ No tables found or error fetching tables")
            return []
            
        # Extract table names and filter out system tables
        tables = []
        for item in response.data:
            schema = item.get('table_schema')
            table_name = item.get('table_name')
            full_name = f"{schema}.{table_name}" if schema != 'public' else table_name
            
            # Skip if table matches any exclude pattern
            if any(re.search(pattern, full_name) for pattern in EXCLUDE_PATTERNS):
                continue
                
            tables.append(full_name)
        
        return sorted(tables)
        
    except Exception as e:
        print(f"❌ Error fetching tables: {e}")
        raise

def get_table_counts(supabase: Client, table_name: str) -> int:
    """Get the number of rows in a table."""
    try:
        result = supabase.table(table_name).select("*", count='exact').execute()
        return result.count or 0
    except Exception as e:
        print(f"⚠️ Error counting rows in {table_name}: {e}")
        return -1

def compare_tables(cloud_tables: List[str], local_tables: List[str], 
                  supabase_cloud: Client, supabase_local: Client) -> None:
    """Compare tables between cloud and local instances."""
    print("\n🔍 Comparing tables between cloud and local instances")
    print("-" * 60)
    print(f"{'Table':<40} {'Cloud Rows':<12} {'Local Rows':<12} Status")
    print("-" * 60)
    
    all_tables = sorted(set(cloud_tables + local_tables))
    
    for table in all_tables:
        cloud_count = get_table_counts(supabase_cloud, table) if table in cloud_tables else "N/A"
        local_count = get_table_counts(supabase_local, table) if table in local_tables else "N/A"
        
        if table not in cloud_tables:
            status = "❌ Only in LOCAL"
        elif table not in local_tables:
            status = "❌ Only in CLOUD"
        elif cloud_count == local_count:
            status = "✅ In sync"
        else:
            status = f"⚠️ Different row counts ({cloud_count} vs {local_count})"
            
        print(f"{table:<40} {str(cloud_count):<12} {str(local_count):<12} {status}")

def show_tables(tables: List[str], instance_name: str, supabase: Client) -> None:
    """Display tables with their row counts."""
    print(f"\n📋 Tables in {instance_name}:")
    print("-" * 60)
    print(f"{'#':<4} {'Table':<40} {'Rows'}")
    print("-" * 60)
    
    for i, table in enumerate(tables, 1):
        count = get_table_counts(supabase, table)
        print(f"{i:<4} {table:<40} {count if count >= 0 else 'Error'}")

def show_menu() -> str:
    """Display the main menu and get user choice."""
    print("\n" + "="*60)
    print("📋 Supabase Migration Tool")
    print("="*60)
    print("1. Show cloud tables")
    print("2. Show local tables")
    print("3. Compare cloud and local")
    print("4. Migrate data from cloud to local")
    print("5. Exit")
    
    while True:
        choice = input("\nChoose an option (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        print("⚠️ Please enter a number between 1 and 5")

def migrate_all_tables(cloud_tables: List[str], supabase_cloud: Client, supabase_local: Client) -> bool:
    """Handle the migration of all tables."""
    if not cloud_tables:
        print("❌ No tables found to migrate")
        return False
        
    print(f"\n📋 Found {len(cloud_tables)} tables to migrate:")
    for i, table in enumerate(cloud_tables, 1):
        print(f"  {i}. {table}")
    
    confirm = input("\nProceed with migration? [y/N] ").strip().lower()
    if confirm != 'y':
        print("\nMigration cancelled by user")
        return False
    
    total_tables = len(cloud_tables)
    for i, table in enumerate(cloud_tables, 1):
        print(f"\n📊 Progress: Table {i} of {total_tables} - {table}")
        try:
            total = migrate_table(supabase_cloud, supabase_local, table)
            print(f"✅ Completed {table}: {total} records migrated")
        except Exception as e:
            print(f"⚠️ Skipping {table} due to error: {e}")
            continue
    
    print("\n🏁 Migration completed!")
    return True

def main():
    """Main migration function with interactive menu."""
    print("🚀 Starting Supabase Migration Tool")
    
    try:
        # Initialize clients
        supabase_cloud, supabase_local = create_supabase_clients()
        
        # Get tables from both instances
        print("\n🔍 Discovering tables...")
        cloud_tables = get_tables(supabase_cloud)
        local_tables = get_tables(supabase_local)
        
        if not cloud_tables and not local_tables:
            print("❌ No tables found in either instance")
            return 1
            
        while True:
            choice = show_menu()
            
            if choice == "1":  # Show cloud tables
                show_tables(cloud_tables, "CLOUD", supabase_cloud)
                
            elif choice == "2":  # Show local tables
                show_tables(local_tables, "LOCAL", supabase_local)
                
            elif choice == "3":  # Compare
                compare_tables(cloud_tables, local_tables, supabase_cloud, supabase_local)
                
            elif choice == "4":  # Migrate
                if not cloud_tables:
                    print("❌ No tables found in cloud instance")
                    continue
                migrate_all_tables(cloud_tables, supabase_cloud, supabase_local)
                # Refresh local tables after migration
                local_tables = get_tables(supabase_local)
                
            elif choice == "5":  # Exit
                print("\n👋 Exiting Supabase Migration Tool")
                return 0
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
