#!/bin/bash
set -e

# Create /data directory if it doesn't exist
mkdir -p /data

# Run migrations
python manage.py migrate

# Start gunicorn
gunicorn config.wsgi:application
