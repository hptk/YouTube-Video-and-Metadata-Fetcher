### Short Introduction

The program ist based on serverside flask and client side angularjs

To install do the following:

		$ python manage.py create_db
		$ python manage.py db init
		$ python manage.py db migrate

Run Redis-Server

		$ redis-server

To run the server do:

		$ python manage.py runserver

Open localhost:5000 in our browser

Start the Celery Worker
		$ celery -A project.celery worker

Start Celery Flower Monitor
		$ celery -A project.celery flower

Go to localhost:5555