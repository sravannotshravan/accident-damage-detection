"""
Debug Login - Test user authentication
"""

import mysql.connector
from config import mysql_credentials
import bcrypt

def test_login():
    print("=" * 60)
    print("🔍 Testing Login Functionality")
    print("=" * 60)
    print()
    
    # First, let's see what users exist
    try:
        connection = mysql.connector.connect(**mysql_credentials)
        cursor = connection.cursor()
        
        print("📋 Checking registered users...")
        cursor.execute("SELECT user_id, name, email, car_brand, model FROM user_info")
        users = cursor.fetchall()
        
        if not users:
            print("⚠️  No users found in database!")
            print("\n💡 You need to sign up first:")
            print("   1. Go to http://localhost:5000/signup")
            print("   2. Create an account")
            print("   3. Then try logging in")
            print()
            connection.close()
            return
        
        print(f"✅ Found {len(users)} user(s):")
        print()
        for user in users:
            print(f"   ID: {user[0]}")
            print(f"   Name: {user[1]}")
            print(f"   Email: {user[2]}")
            print(f"   Vehicle: {user[3]} {user[4]}")
            print(f"   {'-' * 50}")
        
        print()
        print("🔐 Testing Password Authentication...")
        print()
        
        # Get login credentials from user
        test_email = input("Enter email to test: ").strip()
        test_password = input("Enter password to test: ").strip()
        
        # Test login
        cursor.execute("SELECT user_id, name, password FROM user_info WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        
        if result:
            user_id, name, stored_password = result
            print(f"\n✅ User found: {name}")
            print(f"   Stored password (hashed): {stored_password[:50]}...")
            print(f"   Testing password match...")
            
            try:
                # Test password
                if bcrypt.checkpw(test_password.encode('utf-8'), stored_password.encode('utf-8')):
                    print("\n✅ PASSWORD CORRECT!")
                    print(f"   Login should work for: {test_email}")
                else:
                    print("\n❌ PASSWORD INCORRECT!")
                    print("   The password you entered doesn't match.")
            except Exception as e:
                print(f"\n❌ Error checking password: {e}")
                print("   This might indicate a password encryption issue.")
        else:
            print(f"\n❌ No user found with email: {test_email}")
            print("   Please check the email address.")
        
        cursor.close()
        connection.close()
        
        print()
        print("=" * 60)
        
    except mysql.connector.Error as error:
        print(f"❌ Database error: {error}")

if __name__ == "__main__":
    test_login()
