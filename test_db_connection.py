"""
MySQL Database Connection Test Script
Tests connection to local MySQL database for CarDetect AI application
"""

import mysql.connector
from config import mysql_credentials

def test_connection():
    """Test MySQL database connection and display database information"""
    
    print("=" * 60)
    print("🔌 Testing MySQL Database Connection")
    print("=" * 60)
    print()
    
    try:
        # Attempt to connect
        print("📡 Attempting to connect to MySQL...")
        connection = mysql.connector.connect(**mysql_credentials)
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL database!")
            print()
            
            # Get database info
            cursor = connection.cursor()
            
            # Show current database
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"📊 Connected to database: {db_name[0]}")
            print()
            
            # Show MySQL version
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
            print(f"🏷️  MySQL Version: {version[0]}")
            print()
            
            # Check tables
            print("📋 Checking database tables...")
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            if tables:
                table_names = [table[0] for table in tables]
                print(f"✅ Tables found: {', '.join(table_names)}")
                print()
                
                # Check each table
                for table_name in table_names:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    print(f"   📊 {table_name}: {count} records")
                
                print()
                
                # Show table structures
                print("🔍 Table Structures:")
                print("-" * 60)
                for table_name in table_names:
                    print(f"\n📋 {table_name.upper()}:")
                    cursor.execute(f"DESCRIBE {table_name};")
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"   • {col[0]} ({col[1]})")
                
            else:
                print("⚠️  No tables found in database")
                print("   → Run: mysql -u root -p car_damage_detection < db_schema.sql")
            
            print()
            print("-" * 60)
            
            # Test sample queries
            print("\n🧪 Testing Sample Queries...")
            print("-" * 60)
            
            # Test car_models table
            if 'car_models' in table_names:
                cursor.execute("SELECT COUNT(DISTINCT brand) FROM car_models;")
                brand_count = cursor.fetchone()[0]
                print(f"✅ Car brands available: {brand_count}")
                
                cursor.execute("SELECT brand, COUNT(*) as parts FROM car_models GROUP BY brand LIMIT 5;")
                brands = cursor.fetchall()
                print("\n   Sample brands and part counts:")
                for brand in brands:
                    print(f"   • {brand[0]}: {brand[1]} parts")
            
            # Test user_info table
            if 'user_info' in table_names:
                cursor.execute("SELECT COUNT(*) FROM user_info;")
                user_count = cursor.fetchone()[0]
                print(f"\n✅ Registered users: {user_count}")
                
                if user_count > 0:
                    cursor.execute("SELECT name, email, car_brand, model FROM user_info LIMIT 3;")
                    users = cursor.fetchall()
                    print("\n   Sample users:")
                    for user in users:
                        print(f"   • {user[0]} ({user[1]}) - {user[2]} {user[3]}")
            
            print()
            print("=" * 60)
            
            # Close connection
            cursor.close()
            connection.close()
            
            print("\n✅ CONNECTION TEST SUCCESSFUL!")
            print("   Your application is ready to use MySQL database.")
            print()
            
            return True
            
    except mysql.connector.Error as error:
        print(f"\n❌ ERROR: Failed to connect to MySQL database")
        print(f"   Error details: {error}")
        print()
        print("=" * 60)
        print("🔧 TROUBLESHOOTING STEPS:")
        print("=" * 60)
        print()
        print("1. Check if MySQL service is running:")
        print("   PowerShell: Get-Service -Name MySQL80")
        print("   Or: net start MySQL80")
        print()
        print("2. Verify MySQL credentials in config.py:")
        print(f"   Host: {mysql_credentials['host']}")
        print(f"   User: {mysql_credentials['user']}")
        print(f"   Database: {mysql_credentials['database']}")
        print("   Password: [Check if it matches MySQL root password]")
        print()
        print("3. Ensure database exists:")
        print("   mysql -u root -p -e \"CREATE DATABASE IF NOT EXISTS car_damage_detection;\"")
        print()
        print("4. Import database schema:")
        print("   mysql -u root -p car_damage_detection < db_schema.sql")
        print()
        print("5. Check if port 3306 is available:")
        print("   netstat -ano | findstr :3306")
        print()
        print("6. Test MySQL connection manually:")
        print("   mysql -u root -p")
        print()
        
        return False

if __name__ == "__main__":
    test_connection()
