# 🚀 Supabase Cloud to Local Migration Tool

A powerful Python utility designed to simplify and streamline the process of migrating data between Supabase instances. This tool provides an interactive interface for managing your database migrations with confidence.

![Migration Workflow](https://img.shields.io/badge/Status-Production-brightgreen) ![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

- 🔄 **Bidirectional Migration**: Migrate data from cloud to local or between any two Supabase instances
- 🔍 **Smart Table Discovery**: Automatically detects and lists all available tables
- 📊 **Interactive Comparison**: Visually compare table structures and row counts between instances
- ⚡ **Efficient Data Transfer**: Handles large datasets with smart pagination
- 🛡️ **Safe Operations**: Includes confirmation steps and detailed logging
- 🔄 **Progress Tracking**: Real-time updates on migration progress
- 🎯 **Selective Migration**: Choose specific tables to migrate

## 🛠 Installation

### Prerequisites

- Python 3.7 or higher
- Supabase CLI (for local development)
- Access to Supabase project with appropriate permissions

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/supabase-migration.git
   cd supabase-migration
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install them manually:
   ```bash
   pip install python-dotenv supabase
   ```

3. **Configure your environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your Supabase credentials:
   ```env
   # Source Instance (Cloud)
   SUPABASE_CLOUD_URL=https://your-cloud-project.supabase.co
   SUPABASE_CLOUD_KEY=your-cloud-service-role-key

   # Target Instance (Local)
   SUPABASE_LOCAL_URL=http://localhost:54321
   SUPABASE_LOCAL_KEY=your-local-service-role-key
   ```
   
   > ⚠️ **Security Note**: Never commit your `.env` file or expose your service role keys in version control.

## 🚀 Usage

### Starting the Tool

Run the migration tool with:

```bash
python migrate_cloud_to_local.py
```

### Main Menu

You'll be presented with an interactive menu:

```
============================================================
📋 Supabase Migration Tool
============================================================
1. Show cloud tables
2. Show local tables
3. Compare cloud and local
4. Migrate data from cloud to local
5. Exit

Choose an option (1-5): 
```

### Menu Options Explained

#### 1. Show Cloud Tables
- Displays all tables in your cloud instance
- Shows row count for each table
- Helps verify connection to your cloud Supabase

#### 2. Show Local Tables
- Displays all tables in your local instance
- Shows row count for each table
- Verifies connection to your local Supabase

#### 3. Compare Cloud and Local
- Side-by-side comparison of both instances
- Shows synchronization status:
  - ✅ In sync (same row count)
  - ⚠️ Different (different row counts)
  - ❌ Only in [CLOUD/LOCAL] (table missing in one instance)

#### 4. Migrate Data
- Shows tables to be migrated
- Asks for confirmation
- Displays real-time progress
- Shows success/error messages

#### 5. Exit
- Safely exits the application

## 🔧 Advanced Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_CLOUD_URL` | Your cloud Supabase project URL | Required |
| `SUPABASE_CLOUD_KEY` | Cloud service role key | Required |
| `SUPABASE_LOCAL_URL` | Local Supabase URL | `http://localhost:54321` |
| `SUPABASE_LOCAL_KEY` | Local service role key | Required |

### Script Configuration

You can modify these settings in `migrate_cloud_to_local.py`:

```python
# Exclude system tables and auth tables by default
EXCLUDE_PATTERNS = [
    '^pg_',      # PostgreSQL system tables
    '^sql_',     # System tables
    '^_',        # Tables starting with underscore
    '^storage',  # Storage tables
    '^realtime', # Realtime tables
    '^supabase', # Supabase system tables
    '^auth',     # Auth tables
    '^extensions' # Extensions
]

# Include specific schemas (public by default)
INCLUDE_SCHEMAS = ['public']
```

## 📝 Example Output

### Table Comparison
```
🔍 Comparing tables between cloud and local instances
------------------------------------------------------------
Table                              Cloud Rows  Local Rows  Status
------------------------------------------------------------
users                              1500        1000        ⚠️ Different (1500 vs 1000)
products                           42          42          ✅ In sync
customers                           0          N/A         ❌ Only in CLOUD
orders                            500         500          ✅ In sync
```

### Migration Progress
```
🔄 Migrating table: users (1/5)
- Fetched 1000 rows
- Inserted 1000/1500 rows
- Rate: 250 rows/second
✅ Completed users: 1500 records migrated
```

## 🛡️ Security Considerations

1. **Service Role Key**: This key has full access to your database. Never expose it in client-side code.
2. **Environment Variables**: Keep your `.env` file secure and never commit it to version control.
3. **Network Security**: Ensure your Supabase instance has proper network restrictions in place.
4. **Backup**: Always backup your data before performing migrations.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Supabase](https://supabase.com/) for their amazing open-source platform
- [Python Supabase Client](https://github.com/supabase-community/supabase-py) for the Python client library

## Usage

1. Run the migration script:
   ```bash
   python migrate_cloud_to_local.py
   ```

2. You'll see an interactive menu with the following options:
   - **Show cloud tables**: View all tables in your cloud Supabase instance with row counts
   - **Show local tables**: View all tables in your local Supabase instance with row counts
   - **Compare cloud and local**: See a side-by-side comparison of both instances
   - **Migrate data**: Start the migration process
   - **Exit**: Quit the application

3. The migration process will:
   - Show you the list of tables that will be migrated
   - Ask for confirmation before proceeding
   - Display detailed progress for each table
   - Show success/error messages for each operation

### Interactive Menu Options

1. **Show cloud tables**
   - Displays all tables in your cloud Supabase instance
   - Shows row count for each table
   - Helps verify connection to your cloud instance

2. **Show local tables**
   - Displays all tables in your local Supabase instance
   - Shows row count for each table
   - Helps verify connection to your local instance

3. **Compare cloud and local**
   - Shows a side-by-side comparison of both instances
   - Highlights tables that exist in only one instance
   - Shows row count differences for tables in both instances
   - Indicates synchronization status with icons (✅ In sync, ⚠️ Different, ❌ Missing)

4. **Migrate data**
   - Shows list of tables to be migrated
   - Asks for confirmation before starting
   - Displays progress for each table
   - Shows success/error messages
   - Refreshes local table list after migration

### Advanced Configuration

You can customize the migration behavior by modifying these settings in the script:

- `EXCLUDE_PATTERNS`: Regular expressions to exclude specific tables (e.g., system tables)
- `INCLUDE_SCHEMAS`: List of database schemas to include (default: ['public'])

### Keyboard Shortcuts

- `Ctrl+C` - Cancel the current operation and return to the main menu
- `q` - When in table view, return to the main menu

## Example Output

```
🚀 Starting Supabase migration from cloud to local
==============================================

🔄 Migrating table: users
- Copied 1000 records (total: 1000)
- Copied 500 records (total: 1500)
✅ Completed users: 1500 records migrated

🔄 Migrating table: products
- Copied 42 records (total: 42)
✅ Completed products: 42 records migrated

🏁 Migration completed successfully!
```

## Error Handling

The script includes comprehensive error handling:
- Connection errors to Supabase instances
- Individual row insertion errors (logs error but continues)
- Rate limiting protection with delays between requests

## Best Practices

1. **Backup your data** before running migrations
2. Review the list of discovered tables before confirming the migration
3. Run migrations during off-peak hours for production databases
4. Monitor the migration progress and check logs for any errors
5. Use the `EXCLUDE_PATTERNS` to skip system or large tables during initial testing
6. Consider using a VPN or IP allowlisting if your Supabase project has network restrictions

## Troubleshooting

- **Connection Issues**: Verify your Supabase URLs and API keys
- **Permission Errors**: Ensure your service role key has proper permissions
- **Rate Limiting**: If you encounter rate limits, increase the sleep duration in the script

## License

MIT