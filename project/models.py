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

class VideoRepresentation(db.Model):
    __tablename__ = "videoRepresentation"

    video_id = db.Column(db.VARCHAR(12),db.ForeignKey('video.id'),primary_key=True)
    heigth = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer)
    bitrate = db.Column(db.Integer)
    framerate = db.Column(db.Integer)
    codec = db.Column(db.VARCHAR(20))

    def as_dict(self):
        return {
                'heigth':self.heigth,
                'width':self.width,
                'bitrate':self.bitrate,
                'framerate':self.framerate,
                'codec':self.codec
                }

class YoutubeVideo(db.Model):
	__tablename__ = "video"

	id = db.Column(db.VARCHAR(12),primary_key=True,unique=True)
	meta = db.relationship("YoutubeVideoMeta", backref="video", uselist=False)
        representations = db.relationship("VideoRepresentation", backref="video")

	def as_dict(self):
		return {
			'id':self.id,
                        'representations':self.representations.as_dict(),
			'meta':self.meta.as_dict()
			}

class YoutubeVideoMeta(db.Model):
	__tablename__ = "meta"

	id = db.Column(db.VARCHAR(12),db.ForeignKey("video.id"),primary_key=True,unique=True)
	snippet_publishedAt = db.Column(db.DateTime(timezone=True))
	snippet_channel_id = db.Column(db.VARCHAR(50))
	snippet_channel_title = db.Column(db.VARCHAR(100))
	snippet_title = db.Column(db.Text())
	snippet_description = db.Column(db.VARCHAR(5000))
	snippet_category_id = db.Column(db.Integer)
	snippet_tags = db.Column(db.Text())
	snippet_liveBroadcastContent = db.Column(db.VARCHAR(10))
	
	statistics_viewCount = db.Column(db.Integer)
	statistics_likeCount = db.Column(db.Integer)
	statistics_dislikeCount = db.Column(db.Integer)
	#deprecated since august 28, 2015. always set to one
	statistics_favoriteCount = db.Column(db.Integer)
	statistics_commentCount = db.Column(db.Integer)

	status_uploadStatus = db.Column(db.VARCHAR(20))
	status_privacyStatus = db.Column(db.VARCHAR(20))
	status_license = db.Column(db.VARCHAR(20))
	status_embeddable = db.Column(db.BOOLEAN)
	status_publicStatsViewable = db.Column(db.BOOLEAN)

	contentDetails_duration = db.Column(db.Integer)
	contentDetails_dimension = db.Column(db.VARCHAR(2))
	contentDetails_definition = db.Column(db.VARCHAR(2))
	#based on google documentation this field is a string, containing 'true' or 'false', if you want to use boolean instead, you have to manually convert the string into bool
	contentDetails_caption = db.Column(db.String(4))
	#not sure what data type caption should be
	#contentDetails_caption
	contentDetails_licensedContent = db.Column(db.BOOLEAN)
	
	recordingDetails_location_latitude = db.Column(db.Float(precision='10,6'))
	recordingDetails_location_longitude = db.Column(db.Float(precision='10,6'))
	recordingDetails_location_altitude = db.Column(db.Float(precision='10,6'))
	recordingDetails_recordingDate = db.Column(db.DateTime(timezone=True))
	
	def tags_as_dict(self):
		if self.snippet_tags != '':
			return json.loads(self.snippet_tags)
	def as_dict(self):
		return {
			'snippet': {
					'publishedAt':self.snippet_publishedAt,
					'channelId':self.snippet_channel_id,
					'channelTitle':self.snippet_channel_title,
					'title':self.snippet_title,
					'description':self.snippet_description,
					'categoryId':self.snippet_category_id,
					'tags':self.tags_as_dict()
					}
		}

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

	def as_dict(self):
		obj_d = {
			'id': self.id,
			'action': self.action,
			'state': self.state,
			'result': json.loads(self.result),
		}
		return obj_d

class QueryVideoMM(db.Model):
	__tablename__ = "query_video_mm"
	youtube_query_id = db.Column(db.Integer,db.ForeignKey('youtube_queries.id'),primary_key=True)
	video_id = db.Column(db.VARCHAR(12),db.ForeignKey('video.id'),primary_key=True)
	video = db.relationship("YoutubeVideo")

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
			'queryRaw':json.loads(self.queryRaw)
		}
		return obj_d
