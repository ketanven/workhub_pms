import multiprocessing

# Bind to localhost — nginx will proxy to this
bind = "127.0.0.1:8000"

# Workers = (2 × CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout
timeout = 120

# Logging
accesslog = "/var/log/workhub/gunicorn-access.log"
errorlog = "/var/log/workhub/gunicorn-error.log"
loglevel = "info"

# Process naming
proc_name = "workhub"

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50
