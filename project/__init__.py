# project/__init__.py

from flask import Flask, request, jsonify, session,flash, redirect, url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
import project.config
import json
import base64
from sqlalchemy.sql.expression import desc
import logging.config
from redis import ConnectionError
from celery_setup import make_celery

# config
app = Flask(__name__)
app.config.from_object(project.config.BaseConfig)
if 'LOGGING' in app.config:
	logging.config.dictConfig(app.config['LOGGING'])
	

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
celery = make_celery(app)
from project.models import User, APIKey, YoutubeQuery
from tasks import fetch


@app.route('/')
def index():
	return app.send_static_file('index.html')

@app.route('/api/users', methods=['POST'])
def register():
	json_data = request.json 
	user = User(
		firstname=json_data['firstname'],
		lastname=json_data['lastname'],
		username=json_data['username'],
		password=json_data['password']
	)

	try:
		db.session.add(user)
		db.session.commit()

		status = True
	except:
		#this username is already registered
		status = False
	db.session.close()
	return jsonify({'result':status})

@app.route('/api/users/<int:userid>', methods=['GET'])
def getUserByID(userid):
	if(userid==session['id']):
		user = User.query.filter_by(id=userid).first()
		success = True
		user = {'username':user.get_username(),'firstname':user.get_firstname(),'lastname':user.get_lastname()}
	return jsonify({"success":success,"user":user})

@app.route('/api/authenticate', methods=['POST'])
def login():
	json_data = request.json
	message = None
	userid = None
	firstname = None
	lastname = None
	user = User.query.filter_by(username=json_data['username']).first()
	if user and bcrypt.check_password_hash(user.password, json_data['password']):
		session['logged_in'] = True
		session['id'] = user.id
		userid = user.get_id()
		firstname = user.get_firstname()
		lastname = user.get_lastname()
		success = True
	else:
		success = False
		message = "Username or password is incorrect"
	return jsonify({'success': success,'message':message,'userid':userid,'firstname':firstname,'lastname':lastname})

@app.route('/api/logout')
def logout():
	session.pop('logged_in', None)
	return jsonify({'result': 'success'})


@app.route('/api/keys/list', methods=['GET'])
def getAllKeys():
	keys = APIKey.query.filter_by(user_id=session['id']).all()
	dict_keys = [key.as_dict() for key in keys]
	return jsonify({'success': True,'keys':dict_keys})

@app.route('/api/keys', methods=['POST'])
def addAPIKey():
	json_data = request.json 
	apikey = APIKey(
		name=json_data['name'],
		key=json_data['key'],
	)
	try:
		user = User.query.filter_by(id=session['id']).first()
		user.apikeys.append(apikey)
		db.session.commit()
		status = True
	except:
		#key already in use
		status = False
	db.session.close()
	return jsonify({'success':status})

@app.route('/api/keys/<int:keyid>', methods=['DELETE'])
def deleteAPIKey(keyid):
	try:
		APIKey.query.filter_by(id=keyid,user_id=session['id']).delete()
		db.session.commit()
		status = True
	except:
		#dummy
		status = False
	db.session.close()
	return jsonify({'success':status})

@app.route('/api/queries', methods=['POST'])
def createQuery():
	query = YoutubeQuery(
		#experimential, hashing should be changed
		#queryHash=base64.urlsafe_b64encode(json.dumps(request.json)),
		queryHash = "dummy",
		queryRaw=json.dumps(request.json)
	)

	try:
		user = User.query.filter_by(id=session['id']).first()
		user.queries.append(query)
		usedKey = APIKey.query.filter_by(user_id=session['id'],key=request.json['key']).first()
		usedKey.queries.append(query)
		#query.apikey.append(usedKey)
		#query.user.append(user)
		#query.apikey.append(usedKey)
		db.session.commit()
		status = True
		queryId = query.id
		
		
	except:
		#some error
		status = False
	db.session.close()
	return jsonify({'success':status,'id':queryId})

@app.route('/api/queries/<int:id>', methods=['POST'])
def setTask(id):
	json_data = request.json
	action = json_data['action']
	try:
		query = YoutubeQuery.query.filter_by(user_id=session['id'],id=id).first()
		task = fetch.delay(query.get_queryRaw())
		return jsonify({'success':True,'task':{'task_id':task.id, 'task_action':action,'task_action_id':id, 'progress_url':url_for('getProgress',task_action_id=id,task_action=action,task_id=task.id)}})
	except:
		pass
	
@app.route('/api/queries/<int:task_action_id>/<task_action>/progress/<task_id>', methods=['GET'])
def getProgress(task_action_id,task_action,task_id):
	task = fetch.AsyncResult(task_id)
	if task.state == 'PENDING':
		#job did not started yet
		response = {
			'state': task.state, 
			'workedRequests': 0,
			'maxRequests': 0,
			'current':0,
			'queueSize':0,
		}
	elif task.state != 'FAILURE':
		#response = {
		#	'state': task.state,
		#	'workedRequests': task.info.get('workedRequests', 0),
		#	'maxRequests': task.info.get('maxRequests', 0),
		#	'current': task.info.get('current', 0),
		#	'queueSize':task.info.get('queueSize', 0)
		#}
		#if 'result' in task.info:
		#	response['result'] = task.info['result']
		response = task.info
		response['state']=task.state
	else:
		# something went wrong in the background job
		response = {
			'state': task.state,
			'workedRequests': 0,
			'current': 0, 
			'queueSize':0,
			'status': str(task.info)  # this is the exception raised
		}
	return jsonify(response)
   
@app.route('/api/queries/<int:id>', methods=['GET'])
def getQuery(id):
	try:
		query = YoutubeQuery.query.filter_by(user_id=session['id'],id=id).first()
		
		return jsonify({'success': True,'query':json.loads(query.get_queryRaw())})
	except:
		pass
		

@app.route('/api/queries/list/<int:amount>', methods=['GET'])
def getQueries(amount):
	try:
		queries = YoutubeQuery.query.filter_by(user_id=session['id']).order_by(desc(YoutubeQuery.id)).limit(amount)
		dict_queries = [query.as_dict() for query in queries]
		for query in dict_queries:
			query["queryRaw"] = json.loads(query["queryRaw"])
		return jsonify({'success': True,'queries':dict_queries})
	except:
		pass
	
	
@app.errorhandler(ConnectionError)
def connection_error(e):
	debug_description = "<strong>redis-server</strong> is"
	production_description = "both <strong>redis-server</strong> and <strong>worker.py</strong> are"
	description = "Check to make sure that %s running." % (debug_description if app.debug else production_description)
	return description, 500
