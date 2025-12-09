#!/bin/bash

echo "=== Checking open ports on localhost ==="
echo ""

echo "1. Checking PostgreSQL port (5432):"
nc -z localhost 5432
if [ $? -eq 0 ]; then
    echo "   ✓ PostgreSQL is listening on localhost:5432"
else
    echo "   ✗ PostgreSQL is NOT listening on localhost:5432"
fi

echo ""
echo "2. Checking Gunicorn socket:"
if [ -S "/var/www/fefu_lab/web_2025/gunicorn.sock" ]; then
    echo "   ✓ Gunicorn socket exists"
    ls -la /var/www/fefu_lab/web_2025/gunicorn.sock
else
    echo "   ✗ Gunicorn socket does not exist"
fi

echo ""
echo "3. Checking Nginx port (80):"
nc -z localhost 80
if [ $? -eq 0 ]; then
    echo "   ✓ Nginx is listening on localhost:80"
else
    echo "   ✗ Nginx is NOT listening on localhost:80"
fi

echo ""
echo "4. Checking Django development server port (8000):"
nc -z localhost 8000
if [ $? -eq 0 ]; then
    echo "   ⚠️  Django development server is running on port 8000 (should be OFF in production)"
else
    echo "   ✓ Django development server is not running (good for production)"
fi

echo ""
echo "5. Checking from external perspective (simulating host machine):"
echo "   Note: These should fail from external machine"
echo ""
echo "   Testing PostgreSQL from 'external':"
timeout 2 nc -z $(hostname -I | awk '{print $1}') 5432 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ⚠️  WARNING: PostgreSQL is accessible externally!"
else
    echo "   ✓ PostgreSQL is not accessible externally (good)"
fi

echo ""
echo "   Testing Django directly from 'external':"
timeout 2 nc -z $(hostname -I | awk '{print $1}') 8000 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ⚠️  WARNING: Django is accessible on port 8000 externally!"
else
    echo "   ✓ Django is not accessible on port 8000 externally (good)"
fi

echo ""
echo "6. Testing HTTP access via Nginx:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 302 ]; then
    echo "   ✓ HTTP access via Nginx works (status: $HTTP_STATUS)"
    
    # Test static files
    echo ""
    echo "7. Testing static files:"
    curl -s -o /dev/null -w "   Static files: %{http_code}\n" http://localhost/static/fefu_lab/css/style.css
    
    echo ""
    echo "8. Testing admin page:"
    ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/)
    echo "   Admin page status: $ADMIN_STATUS"
else
    echo "   ✗ HTTP access via Nginx failed (status: $HTTP_STATUS)"
fi

echo ""
echo "=== Summary ==="
echo "The application should be accessible only via Nginx on port 80."
echo "PostgreSQL should only accept connections from localhost."
echo "Gunicorn should communicate via Unix socket, not TCP port."
