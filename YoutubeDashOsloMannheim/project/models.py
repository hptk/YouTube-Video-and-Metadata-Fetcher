# project/models.py

import datetime
from project import db,bcrypt
import json
class User(db.Model):
	
	__tablename__ = "users"

	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	firstname = db.Column(db.String(255),nullable=False)
	lastname = db.Column(db.String(255),nullable=False)
	username = db.Column(db.String(255),unique=True,nullable=False)
	password = db.Column(db.String(255),nullable=False)

	queries = db.relationship("YoutubeQuery",backref="user")
	apikeys = db.relationship("APIKey",backref="user")

	def __init__(self,username,password,firstname,lastname):
		self.username = username
		self.password = bcrypt.generate_password_hash(password)
		self.registered_on = datetime.datetime.now()
		self.firstname = firstname
		self.lastname = lastname
	
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False


	def get_id(self):
		return self.id
	def get_username(self):
		return self.username
	def get_firstname(self):
		return self.firstname
	def get_lastname(self):
		return self.lastname

	

class APIKey(db.Model):
	__tablename__ = "apikeys"

	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	name = db.Column(db.String(255),nullable=False)
	key = db.Column(db.String(255),nullable=False,unique=True)
	
	queries = db.relationship("YoutubeQuery",backref="apikeys")
	#query_id = db.Column(db.Integer,db.ForeignKey('queries.id'))
	#query = db.relationship("Query")
	
	def __init__(self,name,key):
		self.name = name
		self.key = key 

	def get_key(self):
		return self.key

	def get_name(self):
		return self.name

	def as_dict(self):
		obj_d = {
			'id': self.id,
			'name': self.name,
			'key': self.key,
		}
		return obj_d

class YoutubeQuery(db.Model):

	__tablename__ = "youtube_queries"

	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	queryHash = db.Column(db.String(255),nullable=False)
	queryRaw = db.Column(db.Text(),nullable=False)
	apikey_id = db.Column(db.Integer,db.ForeignKey('apikeys.id'))
	#apikey_id = db.Column(db.Integer,db.ForeignKey('apikeys.id'))
	#apikey = db.relationship("APIKey",)

	def __init__(self,queryHash,queryRaw):
		self.queryHash = queryHash
		self.queryRaw = queryRaw

	def get_queryHash(self):
		return self.queryHash

	def get_queryRaw(self):
		return self.queryRaw
	def get_queryJson(self):
		return json.dumps(self.queryRaw)
	
	def as_dict(self):
		obj_d = {
			'id':self.id,
			'user_id':self.user_id,
			'queryHash':self.queryHash,
			'queryRaw':self.queryRaw
		}
		return obj_d
