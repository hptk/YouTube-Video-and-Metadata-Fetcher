# manage.py

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from project import app, db, celery

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
def create_sample_data():
	"""Creates sample data"""
	pass
	

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