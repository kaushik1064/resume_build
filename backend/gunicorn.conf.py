# gunicorn.conf.py
import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = 1  # Use 1 worker for AI processing to avoid memory issues
worker_class = "sync"
timeout = 300  # 5 minutes timeout for AI inference
keepalive = 5
max_requests = 100
max_requests_jitter = 10

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
