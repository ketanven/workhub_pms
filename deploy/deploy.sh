#!/bin/bash
set -e

# ============================================
# WorkHub Deployment Script
# Run this on your EC2 instance after setup
# ============================================

APP_DIR="/home/ubuntu/workhub"
BRANCH="${1:-dev}"

echo "=========================================="
echo "  WorkHub Deployment — Branch: $BRANCH"
echo "=========================================="

# 1. Pull latest code
cd "$APP_DIR"
echo "[1/6] Pulling latest code..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# 2. Activate virtualenv & install dependencies
echo "[2/6] Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# 3. Run migrations
echo "[3/6] Running migrations..."
python manage.py migrate --noinput

# 4. Collect static files
echo "[4/6] Collecting static files..."
python manage.py collectstatic --noinput --clear

# 5. Sync permissions (if management command exists)
echo "[5/6] Syncing permissions..."
python manage.py sync_permissions || echo "  (skipped — command not found)"

# 6. Restart services
echo "[6/6] Restarting services..."
sudo systemctl restart workhub
sudo systemctl restart nginx

echo ""
echo "=========================================="
echo "  Deployment complete!"
echo "=========================================="
sudo systemctl status workhub --no-pager -l
