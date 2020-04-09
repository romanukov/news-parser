bind = "0.0.0.0:8000"
workers = 1
worker_class = "gevent"

backlog = 1000
worker_connections = 1000

# max_requests_jitter = 100
# max_requests = 500
timeout = 15
graceful_timeout = 15


def post_fork(server, worker):
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()
