#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/KaliBalIlya/web_fefu_2025.git"
APP_NAME="fefu_lab"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/var/www/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
PROJECT_DIR="$APP_DIR/web_2025"
LOG_DIR="/var/log/gunicorn"
RUN_DIR="/var/run/gunicorn"
DB_NAME="fefu_lab_db"
DB_USER="fefu_user"
DB_PASSWORD="StrongPassword123!"  # Change this in production!

# Function to print colored output
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

print_status "Starting deployment of FEFU Lab application..."

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
print_status "Installing required packages..."
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx curl git supervisor

# Install and configure PostgreSQL
print_status "Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Configure PostgreSQL to only accept local connections
print_status "Securing PostgreSQL..."
PG_CONF="/etc/postgresql/$(ls /etc/postgresql)/main/postgresql.conf"
PG_HBA="/etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf"

# Listen only on localhost
sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = 'localhost'/g" "$PG_CONF"

# Restrict connections to local only
echo "host    $DB_NAME    $DB_USER    127.0.0.1/32    md5" >> "$PG_HBA"
echo "host    $DB_NAME    $DB_USER    ::1/128         md5" >> "$PG_HBA"

# Restart PostgreSQL
systemctl restart postgresql

# Create application directory
print_status "Creating application directory..."
mkdir -p "$APP_DIR"
chown -R $APP_USER:$APP_GROUP "$APP_DIR"

# Clone repository
print_status "Cloning repository..."
cd "$APP_DIR"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Project directory already exists. Updating..."
    cd "$PROJECT_DIR"
    git pull
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    chown -R $APP_USER:$APP_GROUP "$PROJECT_DIR"
fi

# Create virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
chown -R $APP_USER:$APP_GROUP "$VENV_DIR"

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo -u $APP_USER "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u $APP_USER "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

# Create environment file
print_status "Creating environment configuration..."
cat > "$PROJECT_DIR/.env" << EOF
DJANGO_SETTINGS_MODULE=web_2025.settings_production
DJANGO_SECRET_KEY=$(openssl rand -base64 50)
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
EOF

chown $APP_USER:$APP_GROUP "$PROJECT_DIR/.env"
chmod 600 "$PROJECT_DIR/.env"

# Create directories for static and media files
print_status "Creating static and media directories..."
mkdir -p "$PROJECT_DIR/staticfiles" "$PROJECT_DIR/media"
chown -R $APP_USER:$APP_GROUP "$PROJECT_DIR/staticfiles" "$PROJECT_DIR/media"
chmod -R 755 "$PROJECT_DIR/staticfiles" "$PROJECT_DIR/media"

# Create log and run directories for Gunicorn
print_status "Creating log and run directories..."
mkdir -p "$LOG_DIR" "$RUN_DIR"
chown -R $APP_USER:$APP_GROUP "$LOG_DIR" "$RUN_DIR"

# Collect static files
print_status "Collecting static files..."
cd "$PROJECT_DIR"
sudo -u $APP_USER "$VENV_DIR/bin/python" manage.py collectstatic --noinput --settings=web_2025.settings_production

# Apply database migrations
print_status "Applying database migrations..."
sudo -u $APP_USER "$VENV_DIR/bin/python" manage.py makemigrations --settings=web_2025.settings_production
sudo -u $APP_USER "$VENV_DIR/bin/python" manage.py migrate --settings=web_2025.settings_production

# Create superuser if doesn't exist
print_status "Creating superuser..."
sudo -u $APP_USER "$VENV_DIR/bin/python" manage.py shell --settings=web_2025.settings_production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fefu.ru', 'admin123')
    print("Superuser created: admin / admin123")
else:
    print("Superuser already exists")
EOF

# Deploy Gunicorn configuration
print_status "Deploying Gunicorn configuration..."
cp "$PROJECT_DIR/deploy/systemd/gunicorn.service" /etc/systemd/system/
sed -i "s|your-secret-key-change-in-production|$(openssl rand -base64 32)|g" /etc/systemd/system/gunicorn.service
sed -i "s|your-strong-password-here|$DB_PASSWORD|g" /etc/systemd/system/gunicorn.service

systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn

# Deploy Nginx configuration
print_status "Deploying Nginx configuration..."
cp "$PROJECT_DIR/deploy/nginx/fefu_lab.conf" /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/fefu_lab.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx
else
    print_error "Nginx configuration test failed"
    exit 1
fi

# Configure firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    print_status "Configuring firewall..."
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
    ufw --force enable
fi

# Test application
print_status "Testing application..."
sleep 5  # Wait for services to start

# Check Gunicorn status
if systemctl is-active --quiet gunicorn; then
    print_status "Gunicorn is running"
else
    print_error "Gunicorn failed to start"
    systemctl status gunicorn
fi

# Check Nginx status
if systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx failed to start"
    systemctl status nginx
fi

# Test HTTP endpoint
print_status "Testing HTTP endpoint..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 302 ]; then
    print_status "Application is accessible via Nginx (HTTP status: $HTTP_STATUS)"
else
    print_error "Application is not accessible via Nginx (HTTP status: $HTTP_STATUS)"
fi

# Display service status
print_status "Displaying service status..."
echo ""
echo "=== Service Status ==="
systemctl status gunicorn --no-pager
echo ""
systemctl status nginx --no-pager
echo ""
systemctl status postgresql --no-pager

# Display network status
print_status "Checking open ports..."
echo ""
echo "=== Network Status ==="
netstat -tulpn | grep -E ':(80|5432|8000)'

# Final instructions
print_status "Deployment completed!"
echo ""
echo "=== Application Information ==="
echo "Application URL: http://$(hostname -I | awk '{print $1}')"
echo "Admin URL: http://$(hostname -I | awk '{print $1}')/admin/"
echo "Admin credentials: admin / admin123"
echo ""
echo "=== Database Information ==="
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: localhost"
echo "Port: 5432"
echo ""
echo "=== Logs ==="
echo "Gunicorn logs: $LOG_DIR/"
echo "Nginx logs: /var/log/nginx/"
echo "PostgreSQL logs: /var/log/postgresql/"
echo ""
echo "=== Management Commands ==="
echo "Check application status: systemctl status gunicorn"
echo "Restart application: systemctl restart gunicorn"
echo "View application logs: journalctl -u gunicorn -f"
echo "View Nginx logs: tail -f /var/log/nginx/access.log"
