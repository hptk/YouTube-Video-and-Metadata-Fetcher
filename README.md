# YouTubeDashAnalyser

### Web server

The program is accessible through a web interface, running on a local server. The server runs in python 2.7 using [flask](http://flask.pocoo.org/ "flask home page!").

To install and run do the following:

	$ sudo pip2.7 install flask
	$ python2 server.py

Make sure you install flask for python2.7, as this is the level of python this project currently uses. If you don't have pip2.7 you can get it thorugh your normal packet manager (brew/pacman/apt-get etc)

To accesss the now running server go to 

	localhost:5000

You can get comments from a video through

	localhost:5000/getComments/

this gets 50 top comments from PSY's Gangnam Style. you can use

	localhost:5000/getComments/<videoID>

to get the comments of a different video
