# 🗄️ Local MySQL Setup Guide for CarDetect AI

## Quick Guide to Connect Your Application to MySQL on Your Laptop

---

## Step 1: Install MySQL on Windows

### Option A: MySQL Installer (Recommended)

1. **Download MySQL Installer**
   - Go to: https://dev.mysql.com/downloads/installer/
   - Choose: **Windows (x86, 32-bit), MSI Installer** (smaller web installer)
   - Click **Download** → **No thanks, just start my download**

2. **Run MySQL Installer**
   - Choose: **Developer Default** (includes MySQL Server, Workbench, Shell)
   - Or choose: **Server only** (minimal installation)
   - Click **Next** → **Execute** to install

3. **Configure MySQL Server**
   - **Type and Networking**:
     - Config Type: Development Computer
     - Port: **3306** (default)
     - ✅ Open Windows Firewall port
   
   - **Authentication Method**:
     - Choose: **Use Strong Password Encryption**
   
   - **Accounts and Roles**:
     - Root Password: Set a strong password (e.g., `sahilkhan@7824`)
     - ⚠️ **Remember this password!**
   
   - Click **Next** → **Execute** → **Finish**

4. **Verify Installation**
   ```powershell
   # Check if MySQL is running
   Get-Service -Name MySQL80
   
   # Should show: Status = Running
   ```

### Option B: Using Chocolatey (Advanced)

```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install MySQL
choco install mysql -y

# Start MySQL service
net start MySQL80
```

---

## Step 2: Configure MySQL

### Add MySQL to System PATH

1. **Open Environment Variables**:
   - Press `Win + X` → **System** → **Advanced system settings**
   - Click **Environment Variables**

2. **Edit PATH**:
   - Under **System variables**, find and select **Path**
   - Click **Edit** → **New**
   - Add: `C:\Program Files\MySQL\MySQL Server 8.0\bin`
   - Click **OK** → **OK** → **OK**

3. **Restart PowerShell** to apply changes

### Test MySQL Connection

```powershell
# Test MySQL command
mysql --version

# Should show: mysql  Ver 8.0.xx for Win64
```

---

## Step 3: Create Database and Import Schema

### Method 1: Using PowerShell (Recommended)

```powershell
# Navigate to your project directory
cd C:\Users\srava\Documents\GitHub\accident-damage-detection

# Login to MySQL and create database
mysql -u root -p

# Enter your MySQL root password when prompted
```

In MySQL prompt, run:
```sql
-- Create the database
CREATE DATABASE IF NOT EXISTS car_damage_detection;

-- Verify database was created
SHOW DATABASES;

-- Exit MySQL
EXIT;
```

Now import the schema:
```powershell
# Import the database schema
mysql -u root -p car_damage_detection < db_schema.sql

# Enter your password when prompted
```

### Method 2: Using MySQL Workbench (GUI)

1. **Open MySQL Workbench**
2. **Connect** to Local instance (root)
3. **Create Database**:
   - Click **Database** → **Create Schema**
   - Name: `car_damage_detection`
   - Click **Apply** → **Apply** → **Finish**

4. **Import Schema**:
   - Click **File** → **Run SQL Script**
   - Select: `db_schema.sql`
   - Default Schema: `car_damage_detection`
   - Click **Run**

---

## Step 4: Insert Sample Data

```powershell
# Run the Python script to insert spare parts data
python insert_data_into_db.py
```

Or manually import if you have a SQL file:
```powershell
mysql -u root -p car_damage_detection < insert_data.sql
```

---

## Step 5: Verify Database Setup

```powershell
# Login to MySQL
mysql -u root -p

# Switch to your database
USE car_damage_detection;

# Check tables
SHOW TABLES;
# Should show: car_models, user_info

# Check car_models data
SELECT COUNT(*) FROM car_models;
# Should show number of spare parts records

# Check structure
DESCRIBE user_info;
DESCRIBE car_models;

# Exit
EXIT;
```

---

## Step 6: Update Application Configuration

Your `config.py` is already configured correctly:

```python
mysql_credentials = {
    'host': 'localhost',      # ✅ Correct for local MySQL
    'user': 'root',           # ✅ Default MySQL user
    'password': 'sahilkhan@7824',  # ⚠️ Your MySQL password
    'database': 'car_damage_detection'  # ✅ Database name
}
```

### If You Need to Change Password:

Edit `config.py`:
```python
mysql_credentials = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_ROOT_PASSWORD',  # ← Change this
    'database': 'car_damage_detection'
}
```

---

## Step 7: Test Connection from Python

Create a test file to verify connection:

```powershell
# Create test file
New-Item -Path "test_db_connection.py" -ItemType File -Force
```

Add this code to `test_db_connection.py`:
```python
import mysql.connector
from config import mysql_credentials

try:
    # Connect to MySQL
    connection = mysql.connector.connect(**mysql_credentials)
    
    if connection.is_connected():
        print("✅ Successfully connected to MySQL database!")
        
        # Get database info
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"📊 Connected to database: {db_name[0]}")
        
        # Check tables
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM car_models;")
        count = cursor.fetchone()[0]
        print(f"🔧 Spare parts in database: {count}")
        
        cursor.close()
        connection.close()
        print("\n✅ Connection test successful!")
        
except mysql.connector.Error as error:
    print(f"❌ Error connecting to MySQL: {error}")
    print("\n🔧 Troubleshooting:")
    print("1. Check if MySQL service is running: Get-Service MySQL80")
    print("2. Verify password in config.py matches MySQL root password")
    print("3. Ensure database 'car_damage_detection' exists")
    print("4. Check if port 3306 is not blocked by firewall")
```

Run the test:
```powershell
python test_db_connection.py
```

**Expected Output:**
```
✅ Successfully connected to MySQL database!
📊 Connected to database: car_damage_detection
📋 Tables found: ['car_models', 'user_info']
🔧 Spare parts in database: 150

✅ Connection test successful!
```

---

## Step 8: Run Your Application

```powershell
# Make sure you're in the project directory
cd C:\Users\srava\Documents\GitHub\accident-damage-detection

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the application
python app.py
```

Open browser: http://localhost:5000

---

## Common Issues & Solutions

### Issue 1: "Access denied for user 'root'@'localhost'"

**Solution:**
```powershell
# Reset MySQL root password
mysql -u root -p

# In MySQL prompt:
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_new_password';
FLUSH PRIVILEGES;
EXIT;

# Update config.py with new password
```

### Issue 2: "Can't connect to MySQL server on 'localhost'"

**Solution:**
```powershell
# Check if MySQL service is running
Get-Service -Name MySQL80

# If stopped, start it:
Start-Service -Name MySQL80

# Or use:
net start MySQL80
```

### Issue 3: "Database 'car_damage_detection' doesn't exist"

**Solution:**
```powershell
# Create database manually
mysql -u root -p -e "CREATE DATABASE car_damage_detection;"

# Then import schema
mysql -u root -p car_damage_detection < db_schema.sql
```

### Issue 4: "mysql command not found"

**Solution:**
- Add MySQL to PATH (see Step 2)
- Or use full path:
```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

### Issue 5: Port 3306 already in use

**Solution:**
```powershell
# Check what's using port 3306
netstat -ano | findstr :3306

# Kill the process if needed (find PID from above)
taskkill /PID <PID> /F

# Or change MySQL port in my.ini and config.py
```

---

## MySQL Service Management

### Start MySQL Service
```powershell
Start-Service -Name MySQL80
# Or
net start MySQL80
```

### Stop MySQL Service
```powershell
Stop-Service -Name MySQL80
# Or
net stop MySQL80
```

### Restart MySQL Service
```powershell
Restart-Service -Name MySQL80
```

### Check MySQL Status
```powershell
Get-Service -Name MySQL80
```

### Set MySQL to Start Automatically
```powershell
Set-Service -Name MySQL80 -StartupType Automatic
```

---

## Security Best Practices

1. **Change Default Password**
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'strong_password_here';
   ```

2. **Create Application-Specific User** (Recommended)
   ```sql
   -- Login as root
   mysql -u root -p
   
   -- Create new user
   CREATE USER 'cardetect_user'@'localhost' IDENTIFIED BY 'secure_password';
   
   -- Grant permissions
   GRANT ALL PRIVILEGES ON car_damage_detection.* TO 'cardetect_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```
   
   Then update `config.py`:
   ```python
   mysql_credentials = {
       'host': 'localhost',
       'user': 'cardetect_user',      # ← New user
       'password': 'secure_password',  # ← New password
       'database': 'car_damage_detection'
   }
   ```

3. **Use Environment Variables** (Production)
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   mysql_credentials = {
       'host': os.getenv('DB_HOST', 'localhost'),
       'user': os.getenv('DB_USER', 'root'),
       'password': os.getenv('DB_PASSWORD'),
       'database': os.getenv('DB_NAME', 'car_damage_detection')
   }
   ```

---

## Backup Your Database

### Create Backup
```powershell
# Backup entire database
mysqldump -u root -p car_damage_detection > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Backup specific table
mysqldump -u root -p car_damage_detection user_info > user_info_backup.sql
```

### Restore Backup
```powershell
mysql -u root -p car_damage_detection < backup_20241109_143000.sql
```

---

## Quick Reference Commands

```powershell
# Connect to MySQL
mysql -u root -p

# Show databases
SHOW DATABASES;

# Use database
USE car_damage_detection;

# Show tables
SHOW TABLES;

# View table structure
DESCRIBE user_info;

# Count records
SELECT COUNT(*) FROM car_models;

# View all records
SELECT * FROM user_info;

# Delete all users (testing)
DELETE FROM user_info;

# Drop database (careful!)
DROP DATABASE car_damage_detection;
```

---

## Useful MySQL Tools

1. **MySQL Workbench** (GUI) - Included with MySQL installer
2. **phpMyAdmin** - Web-based MySQL administration
3. **DBeaver** - Universal database tool
4. **HeidiSQL** - Lightweight MySQL client

---

## Final Checklist

- [ ] MySQL 8.0 installed on Windows
- [ ] MySQL service running (check with `Get-Service MySQL80`)
- [ ] MySQL added to system PATH
- [ ] Root password set and remembered
- [ ] Database `car_damage_detection` created
- [ ] Schema imported from `db_schema.sql`
- [ ] Sample data inserted (spare parts prices)
- [ ] `config.py` has correct password
- [ ] Connection test successful (`python test_db_connection.py`)
- [ ] Application runs without database errors
- [ ] Can register new user and login

---

## Next Steps

1. ✅ **Test the application**: Create account, upload image
2. 📊 **Monitor database**: Check if records are being saved
3. 🔐 **Secure setup**: Create app-specific MySQL user
4. 💾 **Regular backups**: Schedule weekly database backups
5. 📈 **Optimize**: Add indexes for better performance

---

## Need Help?

If you encounter any issues:

1. **Check MySQL service**: `Get-Service MySQL80`
2. **Test connection**: `python test_db_connection.py`
3. **View logs**: `C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err`
4. **Check port**: `netstat -ano | findstr :3306`

---

**Your Current Configuration:**
- **Host**: localhost
- **User**: root
- **Database**: car_damage_detection
- **Tables**: user_info, car_models
- **Port**: 3306 (default)

**Ready to use!** Just make sure MySQL service is running and password in `config.py` matches your MySQL root password. 🚀
