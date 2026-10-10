"""Gunicorn configuration, loaded automatically from the working directory.

Run with `uv run gunicorn`. Values come from the environment or `.env`; see
`.env.example`.
"""

import multiprocessing
from pathlib import Path

import environ

env = environ.Env()
environ.Env.read_env(Path(__file__).resolve().parent / ".env")

wsgi_app = "config.wsgi:application"

bind = env.list("GUNICORN_BIND", default=["0.0.0.0:8000"])
workers = env.int("WEB_CONCURRENCY", default=multiprocessing.cpu_count() * 2 + 1)
threads = env.int("GUNICORN_THREADS", default=1)
timeout = env.int("GUNICORN_TIMEOUT", default=30)
graceful_timeout = env.int("GUNICORN_GRACEFUL_TIMEOUT", default=30)
keepalive = env.int("GUNICORN_KEEPALIVE", default=5)

max_requests = env.int("GUNICORN_MAX_REQUESTS", default=1000)
max_requests_jitter = env.int("GUNICORN_MAX_REQUESTS_JITTER", default=100)

forwarded_allow_ips = env.str("GUNICORN_FORWARDED_ALLOW_IPS", default="127.0.0.1,::1")

accesslog = "-"
errorlog = "-"
loglevel = env.str("GUNICORN_LOG_LEVEL", default="info")
