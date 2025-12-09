import multiprocessing

# Server socket
bind = 'unix:/var/www/fefu_lab/web_2025/gunicorn.sock'
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 2

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# Process naming
proc_name = 'fefu_lab_gunicorn'

# Server mechanics
daemon = False
pidfile = '/var/run/gunicorn/fefu_lab.pid'
umask = 0
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

# SSL - if needed
# keyfile = ''
# certfile = ''

# Server hooks
def on_starting(server):
    server.log.info("Starting FEFU Lab Gunicorn server...")

def on_exit(server):
    server.log.info("Shutting down FEFU Lab Gunicorn server...")
