# Gunicorn Configuration for Stock Tracking DC
# Based on InvenTree's production configuration

import multiprocessing
import os

# Server Socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Worker Lifecycle
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = 'stockdc-backend'

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("Starting Stock Tracking DC Backend...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("Reloading Stock Tracking DC Backend...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"Stock Tracking DC Backend is ready. Workers: {workers}")

def on_exit(server):
    """Called just before exiting."""
    print("Shutting down Stock Tracking DC Backend...")

# Performance Tuning
preload_app = True  # Load application code before worker processes are forked
worker_tmp_dir = '/dev/shm'  # Use RAM for worker heartbeat (faster than disk)
