# project/models.py

import datetime
from project import db,bcrypt
import json
from sqlalchemy.orm import relationship
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

class YoutubeVideo(db.Model):
	__tablename__ = "video"
	
	id = db.Column(db.VARCHAR(12),primary_key=True,unique=True)
	
class YoutubeVideoMeta(db.Model):
	__tablename__ = "meta"
	
	id = db.Column(db.VARCHAR(12),primary_key=True,unique=True)
	publishedAt = db.Column(db.DateTime(timezone=True))
	channel_id = db.Column(db.VARCHAR(255))
	channel_title = db.Column(db.VARCHAR(255))
	title = db.Column(db.Text())
	description = db.Column(db.Text())
	category_id = db.Column(db.Integer)
	tags = db.Column(db.Text())
	statistics_viewCount = db.Column(db.Integer)
	statistics_likeCount = db.Column(db.Integer)
	statistics_dislikeCount = db.Column(db.Integer)
	statistics_favoriteCount = db.Column(db.Integer)
	statistics_commentCount = db.Column(db.Integer)
	
	status_uploadStatus = db.Column(db.VARCHAR(255))
	status_privacyStatus = db.Column(db.VARCHAR(255))
	status_license = db.Column(db.VARCHAR(255))
	status_embeddable = db.Column(db.BOOLEAN)
	status_publicStatsViewable = db.Column(db.BOOLEAN)
	
	contentDetails_duration = db.Column(db.Integer)
	contentDetails_dimension = db.Column(db.VARCHAR(2))
	contentDetails_definition = db.Column(db.VARCHAR(2))
	#not sure what data type caption should be
	#contentDetails_caption 
	contentDetails_licensedContent = db.Column(db.BOOLEAN)
	
class Task(db.Model):
	__tablename__ = "background_tasks"
	
	id = db.Column(db.VARCHAR(255),primary_key=True)
	action = db.Column(db.VARCHAR(255))
	state = db.Column(db.VARCHAR(255))
	result = db.Column(db.Text())
	query_id = db.Column(db.Integer,db.ForeignKey('youtube_queries.id'))	
	
	def __init__(self,id,action):
		self.id = id
		self.action=action

class QueryVideoMM(db.Model):
	__tablename__ = "query_video_mm"
	youtube_query_id = db.Column(db.Integer,db.ForeignKey('youtube_queries.id'),primary_key=True)
	video_id = db.Column(db.VARCHAR(12),db.ForeignKey('video.id'),primary_key=True)
 
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
	tasks = db.relationship("Task",backref="youtube_queries")
	videos = relationship("QueryVideoMM",backref="queries")
	
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
