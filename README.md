# Short Introduction

## Web server

The program is based on serverside flask and client side angularjs. To use the program the following programs must be installed on your system:

1. python 2.7
2. pip 2.7
3. redis-server

After following the install and run steps below you can access the interface at http://localhost:5000

## Easy install

For a quick and easy install:

		$ ./init.sh

## Running the program

To run:
        $ ./start.sh

to stop:
        $ ./stop.sh

To access the GUI, go to localhost:5000

### Manually running

Run Redis-Server:

		$ redis-server &

Run the server:

		$ python manage.py runserver &

Start the Celery Worker

		$ celery -A project.celery worker &

If oyu want to monitor the worker processes you can use Celery Flower (additional install required):
		$ celery -A project.celery flower


