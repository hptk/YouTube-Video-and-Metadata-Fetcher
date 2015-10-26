# YouTube MetaData and Video Fetcher

### Contents

1. [Web Server](#web-server)
2. [Database](#database)
3. [Downloads](#downloads)
4. [Easy Install](#easy-install)
5. [Running the program](#running-the-program)

## Web Server

The program is based on serverside flask and client side angularjs. To use the program the following programs must be installed on your system:

1. python 2.7
2. pip 2.7
3. redis-server

After following the install and run steps below you can access the interface at 
[localhost:5000](http://localhost:5000).

### Database

The program stores all the results of queries in an sql database. The database is in /project/dev.sqlit

### Downloads

the downloaded video files are stored server-side, storing is as follows:

* In the root folder of this project, a folder '/downloads/' is created
* Inside this folder, a folder is created for each video ID
* Inside each video ID folder, downloaded corresponding files will be placed

File estensions can vary, but the database will have information about file types, codecs and other information that may be needed to use the media files.

Thus, the following pattern emerges:

    Video: /downloads/<videoID>/<videoID>.<resolution>.<extension>
    Sound: /downloads/<videoID>/<videoID>.<extension>

For video files, resolution is the heigth of the media file (1080, 720, etc).

The extensions will be .m4a for audio and m4v for video, if a mp4 representation of the video is available. In the case that only WebM is available, the extensions will be .webm and .webms (s for sound). Again, this information will also be in the corresponding database entry.

## Easy Install

For a quick and easy install:

		$ ./init.sh

## Running the program

To run:

        $ ./start.sh

to stop:

        $ ./stop.sh

### Manually running

Run Redis-Server:

		$ redis-server &

Run the server:

		$ python manage.py runserver &

Start the Celery Worker

		$ celery -A project.celery worker &

If oyu want to monitor the worker processes you can use Celery Flower (additional install required):

		$ celery -A project.celery flower


