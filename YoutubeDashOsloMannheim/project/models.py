# project/models.py

import datetime
from project import db,bcrypt

class User(db.Model):
	
	__tablename__ = "users"

	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	firstname = db.Column(db.String(255),nullable=False)
	lastname = db.Column(db.String(255),nullable=False)
	username = db.Column(db.String(255),unique=True,nullable=False)
	password = db.Column(db.String(255),nullable=False)

	queries = db.relationship("Query")
	apikeys = db.relationship("APIKey")

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

	def __init__(self,user_id,name,key):
		self.user_id = user_id
		self.name = name
		self.key = key 

	def get_key(self):
		return self.key

	def get_name(self):
		return self.name

	def get_user(self):
		return self.user

	def as_dict(self):
		obj_d = {
			'id': self.id,
			'name': self.name,
			'key': self.key,
		}
		return obj_d

class Query(db.Model):

	__tablename__ = "queries"

	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	queryHash = db.Column(db.String(255),nullable=False)
	queryRaws = db.Column(db.String(255),nullable=False)


	def __init__(user,queryHash,queryRaw):
		self.user_id = user_id
		self.queryHash = queryHash
		self.queryRaw = queryRaw

	def get_queryHash(self):
		return self.queryHash

	def get_queryRaw(self):
		return self.queryRaw

