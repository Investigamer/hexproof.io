#!/bin/sh

# Initial Django setup
python manage.py collectstatic
python manage.py migrate

# Hexproof API setup
hexadmin update .
hexadmin sync symbols
hexadmin sync sets

# Run CMD (expose with gunicorn)
exec "$@"
