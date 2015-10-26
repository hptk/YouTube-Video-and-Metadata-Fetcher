## Short Introduction

### Web server

The program ist based on serverside flask and client side angularjs

1. Install libs
2. Install redis-server

To install do the following:

		$ ./init.sh

To run:
        $ ./start.sh

to stop:
        $ ./stop.sh

To access the GUI, go to localhost:5000

Or you can do it manually: 

Run Redis-Server

		$ redis-server

To run the server do:

		$ python manage.py runserver

Open localhost:5000 in our browser

Start the Celery Worker
		$ celery -A project.celery worker

Start Celery Flower Monitor if you want and have it
		$ celery -A project.celery flower


