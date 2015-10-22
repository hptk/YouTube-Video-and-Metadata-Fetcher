ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill
ps auxww | grep 'redis-server' | awk '{print $2}' | xargs kill
ps auxww | grep 'python manage.py runserver' | awk '{print $2}' | xargs kill