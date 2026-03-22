# WorkHub — AWS EC2 Deployment Guide

## Prerequisites
- AWS EC2 instance (Ubuntu 22.04 LTS recommended)
- Security Group: Ports **22** (SSH), **80** (HTTP), **443** (HTTPS) open
- SSH key pair configured
- A domain name (optional, can use EC2 public IP)

---

## Step 1: SSH into EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

---

## Step 2: Install System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    mysql-server libmysqlclient-dev nginx git
```

---

## Step 3: Setup MySQL

```bash
sudo mysql_secure_installation
sudo mysql -u root -p
```

Inside MySQL:
```sql
CREATE DATABASE workhub_staging CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'workhub_user'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON workhub_staging.* TO 'workhub_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## Step 4: Clone the Repository

```bash
cd /home/ubuntu
git clone https://github.com/ketanven/workhub_pms.git workhub
cd workhub
```

---

## Step 5: Setup Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 6: Configure Environment

```bash
cp .env.staging .env
nano .env
```

Fill in your actual values:
- `SECRET_KEY` → Generate one: `python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `ALLOWED_HOSTS` → `your-ec2-public-ip,your-domain.com`
- `DB_NAME` → `workhub_staging`
- `DB_USER` → `workhub_user`
- `DB_PASSWORD` → Your MySQL password
- `CORS_ALLOWED_ORIGINS` → `https://your-frontend-domain.com`

---

## Step 7: Run Migrations & Collect Static

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py sync_permissions
python manage.py seed_admins
```

---

## Step 8: Create Log Directory

```bash
sudo mkdir -p /var/log/workhub
sudo chown ubuntu:ubuntu /var/log/workhub
```

---

## Step 9: Test Gunicorn

```bash
gunicorn --config gunicorn.conf.py workhub.wsgi:application
```

If it starts without errors, press `Ctrl+C` to stop.

---

## Step 10: Setup Systemd Service

```bash
sudo cp deploy/workhub.service /etc/systemd/system/workhub.service
sudo systemctl daemon-reload
sudo systemctl enable workhub
sudo systemctl start workhub
sudo systemctl status workhub
```

---

## Step 11: Setup Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/workhub
sudo ln -sf /etc/nginx/sites-available/workhub /etc/nginx/sites-enabled/workhub
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

> **Important:** Edit `/etc/nginx/sites-available/workhub` and replace `your-domain.com` and `your-ec2-public-ip` with your actual values.

---

## Step 12: Verify

Visit `http://your-ec2-public-ip/api/admin/login/` — you should see the DRF response.

---

## Deploying Updates

After pushing code changes to your branch:

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
cd /home/ubuntu/workhub
bash deploy/deploy.sh dev
```

---

## Optional: SSL with Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Certbot will auto-configure HTTPS in your nginx config.

---

## Useful Commands

| Action | Command |
|--------|---------|
| View logs | `sudo journalctl -u workhub -f` |
| Restart app | `sudo systemctl restart workhub` |
| Restart nginx | `sudo systemctl restart nginx` |
| Check status | `sudo systemctl status workhub` |
| Django shell | `cd /home/ubuntu/workhub && source venv/bin/activate && python manage.py shell` |
