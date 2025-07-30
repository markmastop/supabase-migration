#!/usr/bin/env python3
"""
Supabase Connection Tester
--------------------------
A simple tool to test Supabase connections and list tables.
"""
import os
from typing import Optional, Tuple, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CLOUD_URL = os.getenv("SUPABASE_CLOUD_URL")
CLOUD_KEY = os.getenv("SUPABASE_CLOUD_KEY")
LOCAL_URL = os.getenv("SUPABASE_LOCAL_URL", "http://localhost:54321")
LOCAL_KEY = os.getenv("SUPABASE_LOCAL_KEY", "your-local-service-role-key")

def test_connection(url: str, key: str, name: str) -> Tuple[Optional[Client], bool]:
    """Test connection to a Supabase instance."""
    try:
        print(f"\n🔍 Testing connection to {name}...")
        print(f"URL: {url}")
        
        # Create client
        supabase = create_client(url, key)
        
        # Test connection by listing tables
        print("🔄 Listing tables...")
        tables = list_tables(supabase)
        
        if tables is not None:  # Successfully got tables list
            print(f"✅ Successfully connected to {name}")
            print(f"📋 Found {len(tables)} tables")
            return supabase, True
            
        print(f"⚠️ Connected to {name} but couldn't list tables")
        return supabase, True
        
    except Exception as e:
        error_msg = str(e)
        if 'Failed to establish a new connection' in error_msg:
            print(f"❌ Cannot connect to {name}: Server is not reachable")
        elif 'Invalid API key' in error_msg or 'invalid api key' in error_msg.lower():
            print(f"❌ Invalid API key for {name}")
        elif 'JWT' in error_msg or 'jwt' in error_msg.lower():
            print(f"❌ Authentication failed for {name}: Check your service role key")
        else:
            print(f"❌ Failed to connect to {name}: {error_msg}")
        return None, False

def list_tables(supabase: Client) -> Optional[List[str]]:
    """List all tables in the public schema."""
    try:
        # Try to get tables using information_schema
        response = supabase.rpc('list_tables').execute()
        
        if hasattr(response, 'data') and isinstance(response.data, list):
            table_names = [row['table_name'] for row in response.data if 'table_name' in row]
            return sorted(table_names)
            
        print("⚠️ Could not list tables: Unexpected response format")
        return None
        
    except Exception as e:
        error_msg = str(e)
        if 'function public.list_tables() does not exist' in error_msg or \
           'Could not find the function public.list_tables without parameters' in error_msg:
            print("❌ The 'list_tables' function is not installed in your database.")
            print("\nTo fix this, run the following SQL in your Supabase SQL Editor:")
            print("""
CREATE OR REPLACE FUNCTION public.list_tables()
RETURNS TABLE (table_name text) 
LANGUAGE sql 
SECURITY DEFINER
AS $$
  SELECT tablename::text 
  FROM pg_tables 
  WHERE schemaname = 'public'
$$;
            """)
        else:
            print(f"❌ Error listing tables: {error_msg}")
        return None

def show_menu() -> str:
    """Display the main menu and get user choice."""
    print("\n" + "="*50)
    print("Supabase Migration Toolkit")
    print("="*50)
    print("1. List all source tables")
    print("2. List all target tables")
    print("3. Drop all target tables")
    print("4. Copy table structure from source to target")
    print("5. Copy data from source to target")
    print("6. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ")
        if choice in ["1", "2", "3", "4", "5", "6"]:
            return choice
        print("❌ Invalid choice. Please enter a number between 1 and 6.")

def list_tables_with_counts(supabase: Client, name: str) -> List[str]:
    """List all tables with accurate row counts using pagination."""
    print(f"\n📋 Tables in {name}:")
    tables = list_tables(supabase)
    if not tables:
        print("No tables found.")
        return []

    print(f"\n{'Table':<40} | {'Rows':>10}")
    print("-" * 55)

    for table in tables:
        try:
            total = 0
            batch_size = 1000
            start = 0
            max_empty_batches = 3  # fail-safe for edge cases
            empty_batches = 0

            while True:
                response = supabase.table(table).select("*").range(start, start + batch_size - 1).execute()
                rows = response.data

                if not rows:
                    empty_batches += 1
                    if empty_batches >= max_empty_batches:
                        break
                else:
                    total += len(rows)
                    empty_batches = 0  # reset on valid batch

                if len(rows) < batch_size:
                    break  # last page reached
                start += batch_size

            print(f"{table:<40} | {total:>10,}")

        except Exception as e:
            print(f"{table:<40} | Error: {str(e)}")

    return tables

def drop_tables(supabase: Client, name: str) -> None:
    """Drop all tables in the target database."""
    confirm = input(f"\n⚠️  WARNING: This will drop ALL tables in {name}. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    tables = list_tables(supabase)
    if not tables:
        print("No tables to drop.")
        return
    
    print(f"\nDropping {len(tables)} tables...")
    for table in tables:
        try:
            supabase.rpc('drop_table', {'table_name': table}).execute()
            print(f"✅ Dropped table: {table}")
        except Exception as e:
            print(f"❌ Error dropping table {table}: {e}")

def copy_table_structure(supabase_source: Client, supabase_target: Client) -> None:
    """Copy table structure from source to target."""
    print("\n🔍 Copying table structure...")
    # This is a placeholder - actual implementation would use SQL to get and recreate DDL
    print("Table structure copy not yet implemented")

def copy_table_data(supabase_source: Client, supabase_target: Client) -> None:
    """Copy data from source to target tables."""
    print("\n🔍 Copying table data...")
    tables = list_tables(supabase_source)
    if not tables:
        print("No tables found in source.")
        return
    
    for table in tables:
        try:
            print(f"\n📦 Copying data for table: {table}")
            # Get data from source
            response = supabase_source.table(table).select("*").execute()
            rows = response.data
            
            if not rows:
                print(f"  No data in {table}")
                continue
                
            # Insert into target
            result = supabase_target.table(table).insert(rows).execute()
            print(f"  ✅ Copied {len(rows)} rows to {table}")
            
        except Exception as e:
            print(f"❌ Error copying data for table {table}: {e}")

def main() -> int:
    """Main function with menu system."""
    print("🔌 Supabase Migration Toolkit")
    print("=" * 50)
    
    # Test connections
    supabase_cloud, cloud_ok = test_connection(CLOUD_URL, CLOUD_KEY, "Source (Cloud)")
    supabase_local, local_ok = test_connection(LOCAL_URL, LOCAL_KEY, "Target (Local)")
    
    if not cloud_ok or not local_ok:
        print("\n❌ Please fix the connection issues before continuing.")
        if not cloud_ok:
            print("\nFor Source (Cloud) Supabase:")
            print("- Verify the URL is correct and accessible from your network")
            print("- Check if the service role key is correct")
        if not local_ok:
            print("\nFor Target (Local) Supabase:")
            print("- Make sure your local Supabase instance is running")
            print("  If using Docker: docker compose up -d")
            print("  If using Supabase CLI: supabase start")
            print(f"- Check if the local URL is correct: {LOCAL_URL}")
        return 1
    
    print("\n✅ Both connections are working!")
    
    # Main menu loop
    while True:
        choice = show_menu()
        
        if choice == "1":  # List source tables
            list_tables_with_counts(supabase_cloud, "Source (Cloud)")
            
        elif choice == "2":  # List target tables
            list_tables_with_counts(supabase_local, "Target (Local)")
            
        elif choice == "3":  # Drop target tables
            drop_tables(supabase_local, "Target (Local)")
            
        elif choice == "4":  # Copy table structure
            copy_table_structure(supabase_cloud, supabase_local)
            
        elif choice == "5":  # Copy table data
            copy_table_data(supabase_cloud, supabase_local)
            
        elif choice == "6":  # Exit
            print("\n👋 Goodbye!")
            return 0

if __name__ == "__main__":
    exit(main())
