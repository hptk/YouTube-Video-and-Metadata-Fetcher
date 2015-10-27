#!/usr/bin/env python2.7
# manage.py

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from project import app, db, celery
from project.models import VideoCategory
migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
	"""Creates the db tables"""
	db.create_all()

@manager.command
def drop_db():
	"""Drops the db tables"""
	db.drop_all()
	
@manager.command
def create_categories():
	"""Import the Youtube Video Category List into the database"""
	db.session.add(VideoCategory(1,"UCBR8-60-B28hp2BmDPdntcQ","Film & Animation"))
	db.session.add(VideoCategory(2,"UCBR8-60-B28hp2BmDPdntcQ","Autos & Vehicles"))
	db.session.add(VideoCategory(10,"UCBR8-60-B28hp2BmDPdntcQ","Music"))
	db.session.add(VideoCategory(15,"UCBR8-60-B28hp2BmDPdntcQ","Pets & Animals"))
	db.session.add(VideoCategory(17,"UCBR8-60-B28hp2BmDPdntcQ","Sports"))
	db.session.add(VideoCategory(18,"UCBR8-60-B28hp2BmDPdntcQ","Short Movies"))
	db.session.add(VideoCategory(19,"UCBR8-60-B28hp2BmDPdntcQ","Travel & Events"))
	db.session.add(VideoCategory(20,"UCBR8-60-B28hp2BmDPdntcQ","Gaming"))
	db.session.add(VideoCategory(21,"UCBR8-60-B28hp2BmDPdntcQ","Videoblogging"))
	db.session.add(VideoCategory(22,"UCBR8-60-B28hp2BmDPdntcQ","People & Blogs"))
	db.session.add(VideoCategory(23,"UCBR8-60-B28hp2BmDPdntcQ","Comedy"))
	db.session.add(VideoCategory(24,"UCBR8-60-B28hp2BmDPdntcQ","Entertainment"))
	db.session.add(VideoCategory(25,"UCBR8-60-B28hp2BmDPdntcQ","News & Politics"))
	db.session.add(VideoCategory(26,"UCBR8-60-B28hp2BmDPdntcQ","Howto & Style"))
	db.session.add(VideoCategory(27,"UCBR8-60-B28hp2BmDPdntcQ","Education"))
	db.session.add(VideoCategory(28,"UCBR8-60-B28hp2BmDPdntcQ","Science & Technology"))
	db.session.add(VideoCategory(29,"UCBR8-60-B28hp2BmDPdntcQ","Nonprofits & Activism"))
	db.session.add(VideoCategory(30,"UCBR8-60-B28hp2BmDPdntcQ","Movies"))
	db.session.add(VideoCategory(31,"UCBR8-60-B28hp2BmDPdntcQ","Anime/Animation"))
	db.session.add(VideoCategory(32,"UCBR8-60-B28hp2BmDPdntcQ","Action/Adventure"))
	db.session.add(VideoCategory(33,"UCBR8-60-B28hp2BmDPdntcQ","Classics"))
	db.session.add(VideoCategory(34,"UCBR8-60-B28hp2BmDPdntcQ","Comedy"))
	db.session.add(VideoCategory(35,"UCBR8-60-B28hp2BmDPdntcQ","Documentary"))
	db.session.add(VideoCategory(36,"UCBR8-60-B28hp2BmDPdntcQ","Drama"))
	db.session.add(VideoCategory(37,"UCBR8-60-B28hp2BmDPdntcQ","Family"))
	db.session.add(VideoCategory(38,"UCBR8-60-B28hp2BmDPdntcQ","Foreign"))
	db.session.add(VideoCategory(39,"UCBR8-60-B28hp2BmDPdntcQ","Horror"))
	db.session.add(VideoCategory(40,"UCBR8-60-B28hp2BmDPdntcQ","Sci-Fi/Fantasy"))
	db.session.add(VideoCategory(41,"UCBR8-60-B28hp2BmDPdntcQ","Thriller"))
	db.session.add(VideoCategory(42,"UCBR8-60-B28hp2BmDPdntcQ","Shorts"))
	db.session.add(VideoCategory(43,"UCBR8-60-B28hp2BmDPdntcQ","Shows"))
	db.session.add(VideoCategory(44,"UCBR8-60-B28hp2BmDPdntcQ","Trailers"))
	db.session.commit()
	
if __name__ == '__main__':
	debug = app.config.get('DEBUG',True)
	#argv = [
    #    'worker',
    #    '--loglevel=DEBUG',
    #    '&'
    #]
	#celery.worker_main(argv)
	#celery.start(argv=['celery', 'worker', '-l', 'info'])
	#celery.start()
	#from project.worker import TaskWorker
	#worker = TaskWorker(app,debug=debug)
	#worker.reset()
	#worker.start()
	manager.run()

