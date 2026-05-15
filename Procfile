web: gunicorn config.wsgi:application --log-file -
web: python manage.py migrate && gunicorn config.wsgi
