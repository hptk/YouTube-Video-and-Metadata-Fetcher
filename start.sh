redis-server &
celery -A project.celery worker &
python manage.py runserver &