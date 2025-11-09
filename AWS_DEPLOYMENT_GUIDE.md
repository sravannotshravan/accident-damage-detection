# 🚀 AWS Deployment Guide for CarDetect AI

## Complete Guide to Deploy Vehicle Damage Detection Application on AWS

---

## 📋 Table of Contents

1. [Deployment Options Overview](#deployment-options-overview)
2. [Prerequisites](#prerequisites)
3. [Option 1: AWS EC2 Deployment](#option-1-aws-ec2-deployment-recommended)
4. [Option 2: AWS Elastic Beanstalk](#option-2-aws-elastic-beanstalk)
5. [Option 3: AWS ECS with Docker](#option-3-aws-ecs-with-docker)
6. [Database Setup (RDS)](#database-setup-aws-rds)
7. [File Storage (S3)](#file-storage-aws-s3)
8. [Domain & SSL Setup](#domain--ssl-setup)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Cost Optimization](#cost-optimization)

---

## Deployment Options Overview

| Option | Difficulty | Cost | Scalability | Best For |
|--------|-----------|------|-------------|----------|
| **EC2** | Medium | $10-50/mo | Manual | Full control, learning |
| **Elastic Beanstalk** | Easy | $20-70/mo | Auto | Quick deployment |
| **ECS/Docker** | Hard | $30-100/mo | Auto | Production apps |

**Recommendation**: Start with **EC2** for learning, move to **Elastic Beanstalk** for production.

---

## Prerequisites

### 1. AWS Account Setup
- [ ] Create AWS account at https://aws.amazon.com/
- [ ] Set up billing alerts
- [ ] Enable MFA for security
- [ ] Create IAM user (don't use root account)

### 2. Local Requirements
- [ ] Install AWS CLI: https://aws.amazon.com/cli/
- [ ] Install Git
- [ ] Have your project code ready
- [ ] Database schema ready (db_schema.sql)

### 3. AWS CLI Configuration
```bash
# Install AWS CLI (Windows)
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Configure AWS CLI
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format: json
```

### 4. Generate SSH Key Pair
```bash
# For Windows (PowerShell)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Save to: C:\Users\YourName\.ssh\aws_key
```

---

## Option 1: AWS EC2 Deployment (Recommended)

### Step 1: Launch EC2 Instance

#### 1.1 Create EC2 Instance
1. Go to **AWS Console** → **EC2** → **Launch Instance**
2. Configure:
   - **Name**: `cardetect-ai-app`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: `t2.medium` (recommended for ML) or `t2.micro` (free tier)
   - **Key Pair**: Create new or select existing
   - **Network Settings**:
     - Auto-assign public IP: **Enable**
     - Security Group: Create new
   - **Storage**: 30 GB gp3 (minimum for ML models)

#### 1.2 Configure Security Group
Create security group with these rules:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web traffic |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure web |
| Custom TCP | TCP | 5000 | 0.0.0.0/0 | Flask (temporary) |

**Launch Instance** → Wait for status to be "Running"

---

### Step 2: Connect to EC2 Instance

```bash
# Windows PowerShell
ssh -i "C:\Users\YourName\.ssh\your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP

# If permission error on Windows:
icacls "C:\Users\YourName\.ssh\your-key.pem" /inheritance:r
icacls "C:\Users\YourName\.ssh\your-key.pem" /grant:r "%username%:R"
```

---

### Step 3: Setup Server Environment

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.10 python3-pip python3-venv nginx git

# Install system dependencies for OpenCV and ML
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev

# Install MySQL client
sudo apt install -y mysql-client libmysqlclient-dev

# Verify installations
python3 --version
pip3 --version
nginx -v
```

---

### Step 4: Clone and Setup Application

```bash
# Create application directory
cd /home/ubuntu
mkdir -p apps
cd apps

# Clone your repository
git clone https://github.com/sravannotshravan/accident-damage-detection.git
cd accident-damage-detection

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# If requirements.txt fails, install manually:
pip install Flask==3.1.0 \
    bcrypt==4.2.0 \
    mysql-connector-python==9.1.0 \
    python-dotenv==1.0.1 \
    ultralytics==8.3.32 \
    opencv-python==4.10.0.84 \
    Werkzeug==3.1.3
```

---

### Step 5: Configure Environment Variables

```bash
# Create .env file
nano .env

# Add these variables:
SECRET_KEY=your-super-secret-key-change-this-in-production
DB_HOST=your-rds-endpoint.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-strong-password
DB_NAME=cardetect_db
```

**Generate secure secret key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### Step 6: Setup MySQL Database on AWS RDS

#### 6.1 Create RDS Instance
1. Go to **AWS Console** → **RDS** → **Create Database**
2. Configure:
   - **Engine**: MySQL 8.0
   - **Template**: Free tier (or Production for production)
   - **DB Instance**: `cardetect-db`
   - **Master Username**: `admin`
   - **Master Password**: Create strong password
   - **Instance Configuration**: db.t3.micro (free tier)
   - **Storage**: 20 GB
   - **Public Access**: Yes (for initial setup, change later)
   - **VPC Security Group**: Create new
   - **Database Name**: `cardetect_db`

#### 6.2 Configure RDS Security Group
Add inbound rule:
- **Type**: MySQL/Aurora (3306)
- **Source**: EC2 Security Group ID

#### 6.3 Import Database Schema
```bash
# From your EC2 instance
mysql -h your-rds-endpoint.amazonaws.com -u admin -p cardetect_db < db_schema.sql

# Insert initial data
mysql -h your-rds-endpoint.amazonaws.com -u admin -p cardetect_db < insert_data_into_db.py
# Or run the Python script
python3 insert_data_into_db.py
```

---

### Step 7: Update Application Configuration

```bash
# Edit config.py
nano config.py
```

Update database credentials:
```python
import os
from dotenv import load_dotenv

load_dotenv()

mysql_credentials = {
    'host': os.getenv('DB_HOST', 'your-rds-endpoint.amazonaws.com'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'cardetect_db')
}
```

---

### Step 8: Configure Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn config
nano gunicorn_config.py
```

Add this content:
```python
# gunicorn_config.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
errorlog = "/home/ubuntu/apps/accident-damage-detection/logs/gunicorn_error.log"
accesslog = "/home/ubuntu/apps/accident-damage-detection/logs/gunicorn_access.log"
loglevel = "info"
```

Create logs directory:
```bash
mkdir -p logs
```

---

### Step 9: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/cardetect.service
```

Add this content:
```ini
[Unit]
Description=CarDetect AI Flask Application
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/apps/accident-damage-detection
Environment="PATH=/home/ubuntu/apps/accident-damage-detection/venv/bin"
ExecStart=/home/ubuntu/apps/accident-damage-detection/venv/bin/gunicorn \
    --config /home/ubuntu/apps/accident-damage-detection/gunicorn_config.py \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cardetect
sudo systemctl start cardetect
sudo systemctl status cardetect
```

---

### Step 10: Configure Nginx as Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/cardetect
```

Add this content:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    client_max_body_size 20M;

    # Static files
    location /static {
        alias /home/ubuntu/apps/accident-damage-detection/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120;
        proxy_send_timeout 120;
        proxy_read_timeout 120;
    }
}
```

Enable the site:
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/cardetect /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

### Step 11: Test Your Application

```bash
# Check if services are running
sudo systemctl status cardetect
sudo systemctl status nginx

# Test locally
curl http://localhost

# From browser
http://YOUR_EC2_PUBLIC_IP
```

---

### Step 12: Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

Update Nginx config will be automatic, or manually:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Rest of configuration...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Option 2: AWS Elastic Beanstalk

### Prerequisites
```bash
# Install EB CLI
pip install awsebcli
```

### Step 1: Prepare Application

Create `.ebextensions/01_packages.config`:
```yaml
packages:
  yum:
    git: []
    mysql-devel: []
    
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app/current
```

Create `.ebignore`:
```
venv/
.venv/
__pycache__/
*.pyc
.env
.git/
.DS_Store
```

### Step 2: Initialize and Deploy

```bash
# Initialize EB application
eb init -p python-3.10 cardetect-ai --region us-east-1

# Create environment
eb create cardetect-env \
    --instance-type t2.medium \
    --database \
    --database.engine mysql \
    --database.username admin

# Set environment variables
eb setenv SECRET_KEY=your-secret-key \
    DB_HOST=your-rds-endpoint \
    DB_USER=admin \
    DB_PASSWORD=your-password

# Deploy
eb deploy

# Open in browser
eb open
```

### Step 3: Configure Scaling (Optional)

```bash
# Auto-scaling configuration
eb scale 2  # Run 2 instances

# Or use configuration file
eb config
```

---

## Option 3: AWS ECS with Docker

### Step 1: Create Dockerfile

Create `Dockerfile` in project root:
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p static logs

# Expose port
EXPOSE 8000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "app:app"]
```

Create `.dockerignore`:
```
.git
.gitignore
venv/
.venv/
__pycache__/
*.pyc
.env
README.md
*.md
.vscode/
```

### Step 2: Build and Push to ECR

```bash
# Install Docker (if not installed)
# Follow: https://docs.docker.com/get-docker/

# Build image
docker build -t cardetect-ai .

# Test locally
docker run -p 8000:8000 --env-file .env cardetect-ai

# Create ECR repository
aws ecr create-repository --repository-name cardetect-ai --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag cardetect-ai:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cardetect-ai:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cardetect-ai:latest
```

### Step 3: Create ECS Cluster and Service

1. Go to **AWS Console** → **ECS** → **Create Cluster**
2. Select **EC2 Linux + Networking**
3. Configure cluster:
   - **Cluster name**: `cardetect-cluster`
   - **Instance type**: `t2.medium`
   - **Number of instances**: 2
   - **Key pair**: Select your key

4. Create Task Definition:
   - **Launch type**: EC2
   - **Task memory**: 2048 MB
   - **Task CPU**: 1024
   - Add container:
     - **Name**: `cardetect-app`
     - **Image**: Your ECR image URI
     - **Memory**: 2048
     - **Port mappings**: 8000:8000

5. Create Service:
   - **Launch type**: EC2
   - **Task Definition**: Select created task
   - **Service name**: `cardetect-service`
   - **Number of tasks**: 2
   - **Load balancer**: Application Load Balancer

---

## Database Setup (AWS RDS)

### Complete RDS Configuration

```bash
# Create parameter group for optimization
aws rds create-db-parameter-group \
    --db-parameter-group-name cardetect-params \
    --db-parameter-group-family mysql8.0 \
    --description "CarDetect AI MySQL parameters"

# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier cardetect-db \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --engine-version 8.0.35 \
    --master-username admin \
    --master-user-password YourStrongPassword123! \
    --allocated-storage 20 \
    --db-name cardetect_db \
    --backup-retention-period 7 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --publicly-accessible \
    --storage-encrypted
```

### Database Migration

```bash
# Export local database
mysqldump -u root -p cardetect_db > backup.sql

# Import to RDS
mysql -h your-rds-endpoint.amazonaws.com -u admin -p cardetect_db < backup.sql
```

---

## File Storage (AWS S3)

### Setup S3 for Static Files

```bash
# Create S3 bucket
aws s3 mb s3://cardetect-ai-uploads --region us-east-1

# Set bucket policy for public read
aws s3api put-bucket-policy --bucket cardetect-ai-uploads --policy file://bucket-policy.json
```

Create `bucket-policy.json`:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::cardetect-ai-uploads/*"
        }
    ]
}
```

### Update Application to Use S3

Install boto3:
```bash
pip install boto3
```

Update `app.py`:
```python
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

BUCKET_NAME = 'cardetect-ai-uploads'

def upload_to_s3(file_path, object_name):
    try:
        s3_client.upload_file(file_path, BUCKET_NAME, object_name)
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{object_name}"
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None
```

---

## Domain & SSL Setup

### 1. Register Domain (Route 53)

```bash
# Check domain availability
aws route53domains check-domain-availability --domain-name yoursite.com

# Register domain (costs ~$12/year)
aws route53domains register-domain \
    --domain-name yoursite.com \
    --duration-in-years 1 \
    --admin-contact file://contact.json \
    --registrant-contact file://contact.json \
    --tech-contact file://contact.json
```

### 2. Create Hosted Zone

```bash
aws route53 create-hosted-zone \
    --name yoursite.com \
    --caller-reference $(date +%s)
```

### 3. Point Domain to EC2

1. Get your EC2 Elastic IP
2. Create A record in Route 53
3. Wait for DNS propagation (5-30 minutes)

---

## Monitoring & Maintenance

### CloudWatch Logging

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Monitoring Commands

```bash
# Check application logs
sudo journalctl -u cardetect -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check application logs
tail -f /home/ubuntu/apps/accident-damage-detection/logs/gunicorn_error.log

# Check system resources
htop
df -h
free -m
```

### Backup Strategy

```bash
# Automated backup script
nano /home/ubuntu/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -h your-rds-endpoint.amazonaws.com -u admin -p$DB_PASSWORD cardetect_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup files
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /home/ubuntu/apps/accident-damage-detection/static

# Upload to S3
aws s3 cp $BACKUP_DIR/ s3://cardetect-ai-backups/ --recursive

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -mtime +7 -delete
```

Make executable and schedule:
```bash
chmod +x /home/ubuntu/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /home/ubuntu/backup.sh
```

---

## Cost Optimization

### Estimated Monthly Costs

**Minimal Setup (Free Tier Eligible):**
- EC2 t2.micro: $0 (free tier)
- RDS db.t3.micro: $0 (free tier)
- Data Transfer: ~$1
- **Total: ~$1/month** (first year)

**Production Setup:**
- EC2 t2.medium: $34/month
- RDS db.t3.small: $25/month
- ALB: $16/month
- S3 Storage: $2/month
- Data Transfer: $5/month
- **Total: ~$82/month**

### Cost Saving Tips

1. **Use Reserved Instances** (save 30-70%)
2. **Stop EC2 when not in use** (development)
3. **Use S3 Lifecycle policies** (move old files to Glacier)
4. **Enable CloudWatch alarms** (billing alerts)
5. **Right-size instances** (use smallest that works)
6. **Use Spot Instances** for non-critical workloads

---

## Troubleshooting

### Common Issues

**1. Application won't start:**
```bash
# Check service status
sudo systemctl status cardetect

# View logs
sudo journalctl -u cardetect -n 100

# Test manually
cd /home/ubuntu/apps/accident-damage-detection
source venv/bin/activate
python app.py
```

**2. Database connection issues:**
```bash
# Test connection
mysql -h your-rds-endpoint.amazonaws.com -u admin -p

# Check security group rules
# Ensure EC2 can access RDS on port 3306
```

**3. Nginx 502 Bad Gateway:**
```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Restart services
sudo systemctl restart cardetect
sudo systemctl restart nginx
```

**4. Out of memory:**
```bash
# Check memory
free -m

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Security Best Practices

1. **Use IAM roles** instead of hardcoded credentials
2. **Enable MFA** on AWS account
3. **Restrict Security Groups** (use specific IPs)
4. **Regular updates**: `sudo apt update && sudo apt upgrade`
5. **Use HTTPS** (SSL/TLS) - Let's Encrypt
6. **Enable CloudTrail** (audit logging)
7. **Backup database** regularly
8. **Use AWS Secrets Manager** for sensitive data
9. **Enable WAF** (Web Application Firewall)
10. **Regular security audits**

---

## Deployment Checklist

- [ ] AWS account created and configured
- [ ] EC2 instance launched and running
- [ ] Security groups configured
- [ ] SSH access working
- [ ] Application code cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] RDS database created
- [ ] Database schema imported
- [ ] Environment variables set
- [ ] Gunicorn configured
- [ ] Systemd service created and running
- [ ] Nginx installed and configured
- [ ] Domain pointed to EC2 (optional)
- [ ] SSL certificate installed (optional)
- [ ] Application accessible via browser
- [ ] File uploads working
- [ ] Damage detection working
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Documentation updated

---

## Next Steps After Deployment

1. **Test thoroughly** - All features, edge cases
2. **Monitor performance** - CloudWatch, logs
3. **Optimize** - Database queries, caching
4. **Scale** - Add load balancer if needed
5. **Secure** - Regular security updates
6. **Backup** - Automated daily backups
7. **Document** - Keep deployment notes
8. **CI/CD** - Setup automated deployments (GitHub Actions)

---

## Support & Resources

### AWS Documentation
- [EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [RDS User Guide](https://docs.aws.amazon.com/rds/)
- [Elastic Beanstalk Guide](https://docs.aws.amazon.com/elasticbeanstalk/)

### Useful Commands
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@ec2-ip

# Check application status
sudo systemctl status cardetect

# View logs
sudo journalctl -u cardetect -f

# Restart application
sudo systemctl restart cardetect

# Update code
cd /home/ubuntu/apps/accident-damage-detection
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart cardetect
```

---

## Conclusion

You now have a complete guide to deploy your CarDetect AI application on AWS! Start with the EC2 deployment for learning, then scale to production-grade solutions as needed.

**Estimated Setup Time:**
- EC2 Deployment: 1-2 hours
- Elastic Beanstalk: 30 minutes - 1 hour
- ECS/Docker: 2-3 hours

**Good luck with your deployment!** 🚀

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Author**: CarDetect AI Team
