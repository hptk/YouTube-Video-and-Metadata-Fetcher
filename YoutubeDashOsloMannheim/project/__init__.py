# project/__init__.py

from flask import Flask, request, jsonify, session, redirect
from flask.ext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
from project.config import BaseConfig
import json
import base64
from sqlalchemy.sql.expression import desc
# config
app = Flask(__name__)
app.config.from_object(BaseConfig)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from project.models import User, APIKey, YoutubeQuery

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