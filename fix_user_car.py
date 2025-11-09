"""
Update user's car model to match database
"""

import mysql.connector
from config import mysql_credentials

conn = mysql.connector.connect(**mysql_credentials)
cursor = conn.cursor()

# Update user's car model to Swift (which exists in database)
cursor.execute(
    'UPDATE user_info SET model = %s WHERE email = %s',
    ('Swift', 'sravan.kowshik@outlook.com')
)
conn.commit()

print("✅ Updated your car model from 'Alto K10' to 'Swift'")
print("   Now prices will show when you upload images!")
print()
print("   Try uploading a vehicle image again.")

conn.close()
