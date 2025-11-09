"""
Database Setup Script
Creates the database and imports the schema
"""

import mysql.connector
from config import mysql_credentials

def setup_database():
    """Create database and import schema"""
    
    print("=" * 60)
    print("🔧 Setting Up Database")
    print("=" * 60)
    print()
    
    # Connect without specifying database (to create it)
    try:
        print("📡 Connecting to MySQL server...")
        connection = mysql.connector.connect(
            host=mysql_credentials['host'],
            user=mysql_credentials['user'],
            password=mysql_credentials['password']
        )
        
        cursor = connection.cursor()
        
        # Create database
        print(f"📊 Creating database: {mysql_credentials['database']}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_credentials['database']}")
        print("✅ Database created successfully!")
        
        # Switch to the database
        cursor.execute(f"USE {mysql_credentials['database']}")
        
        # Read and execute schema file
        print("\n📋 Creating tables...")
        with open('db_schema.sql', 'r') as f:
            sql_commands = f.read()
        
        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        for command in commands:
            if command.upper().startswith(('CREATE', 'INSERT', 'ALTER')):
                try:
                    cursor.execute(command)
                    if 'CREATE TABLE' in command.upper():
                        # Extract table name
                        table_name = command.split('TABLE')[1].split('(')[0].strip().replace('IF NOT EXISTS', '').strip()
                        print(f"   ✅ Created table: {table_name}")
                except mysql.connector.Error as e:
                    if 'already exists' not in str(e):
                        print(f"   ⚠️  Warning: {e}")
        
        connection.commit()
        
        # Verify tables
        print("\n📋 Verifying tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print("✅ Tables in database:")
            for table in tables:
                print(f"   • {table[0]}")
                
                # Show structure
                cursor.execute(f"DESCRIBE {table[0]}")
                columns = cursor.fetchall()
                print(f"     Columns: {len(columns)}")
        else:
            print("⚠️  No tables found!")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run: python insert_data_into_db.py  (to add spare parts data)")
        print("2. Run: python test_db_connection.py   (to verify everything)")
        print("3. Run: python app.py                  (to start your application)")
        print()
        
        return True
        
    except mysql.connector.Error as error:
        print(f"\n❌ ERROR: {error}")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("1. Make sure MySQL is installed and running")
        print("2. Check password in config.py matches your MySQL root password")
        print("3. Try connecting manually: mysql -u root -p")
        print()
        return False

if __name__ == "__main__":
    setup_database()
