# project/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(basedir,'../data')


class BaseConfig(object):
	SECRET_KEY = 'tc7NG9RbAMhV3rLUj8RwF2rzu7BZLbQ5'
	DEBUG = True
	BCRYPT_LOG_ROUNDS = 13
	SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(datadir,'database.sqlite')
	REDIS_QUEUE_KEY = 'youtube-teleseminar'
	# Logging defaults
	LOGGING = {
		'version': 1,
		'handlers': { 'console': { 'level': 'DEBUG', 'class': 'logging.StreamHandler', } },
		'loggers': { 'tasks': { 'handlers': ['console'], 'level': 'DEBUG', } }
	}
	CELERY_BROKER_URL='redis://localhost:6379/0'
	CELERY_RESULT_BACKEND='redis://localhost:6379/0'
	#dont use sqlite result backend. It is much slower since we are doing a lot of status updates in our tasks
	#CELERY_RESULT_BACKEND='db+sqlite:///'+os.path.join(basedir,'dev.sqlite')