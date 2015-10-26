# project/models.py

import datetime
from project import db
import json
from sqlalchemy.orm import relationship
import hashlib
import base64
from project.config import BaseConfig
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
        self.password = hashlib.sha512(password+BaseConfig.SECRET_KEY).hexdigest()
        self.firstname = firstname
        self.lastname = lastname
    
    def comparePassword(self,password):
        if self.password == hashlib.sha512(password+BaseConfig.SECRET_KEY).hexdigest():
            return True
        else:
            return False
        
class VideoRepresentation(db.Model):
    __tablename__ = "videoRepresentation"

    video_id = db.Column(db.VARCHAR(12),db.ForeignKey('video.id'),primary_key=True)
    mimeType = db.Column(db.VARCHAR(15))
    height = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer)
    bitrate = db.Column(db.Integer)
    framerate = db.Column(db.Integer)
    codec = db.Column(db.VARCHAR(20))

    def __init__(self, video_id, mimeType, bitrate, codec, framerate=0, height=0, width=0):
        self.video_id = video_id
        self.mimeType = mimeType
        self.bitrate = bitrate
        self.codec = codec
        self.framerate = framerate
        self.height = height
        self.width = width
        
    def as_dict(self):
        return {
                'mimeType':self.mimeType,
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
    
    def is_meta_available(self):
        if self.meta != None:
            return 1
        else:
            return 0
        
    def __init__(self, id, meta, representation):
        self.id = id
        self.meta = meta
        self.representation = representation

    def as_dict(self):
        return {
            'id':self.id,
            #'representations':self.representations.as_dict(),
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
    #deprecated since august 28, 2015. always set to zero
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
    contentDetails_licensedContent = db.Column(db.BOOLEAN)
    
    recordingDetails_location_latitude = db.Column(db.Float(precision='10,6'))
    recordingDetails_location_longitude = db.Column(db.Float(precision='10,6'))
    recordingDetails_location_altitude = db.Column(db.Float(precision='10,6'))
    recordingDetails_recordingDate = db.Column(db.DateTime(timezone=True))
    
    def as_dict(self):
        return {
            'snippet': {
                    'publishedAt':self.snippet_publishedAt,
                    'channelId':self.snippet_channel_id,
                    'channelTitle':self.snippet_channel_title,
                    'title':self.snippet_title,
                    'description':self.snippet_description,
                    'categoryId':self.snippet_category_id,
                    'tags':json.loads(self.snippet_tags) if self.snippet_tags != '' else None
                    }
        }

class Task(db.Model):
    __tablename__ = "background_tasks"

    id = db.Column(db.VARCHAR(255),primary_key=True)
    action = db.Column(db.VARCHAR(255))
    state = db.Column(db.VARCHAR(255))
    result = db.Column(db.Text())
    created_on = db.Column(db.DateTime(timezone=True))
    query_id = db.Column(db.Integer,db.ForeignKey('youtube_queries.id'))

    def __init__(self,id,action):
        self.id = id
        self.action=action
        self.created_on = datetime.datetime.now()

    def as_dict(self):        
        return {
            'id': self.id,
            'created_on':self.created_on,
            'action': self.action,
            'state': self.state,
            'result': json.loads(self.result) if self.result is not None else None
        }

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

    def __init__(self,name,key):
        self.name = name
        self.key = key

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
        }

class YoutubeQuery(db.Model):

    __tablename__ = "youtube_queries"

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    queryHash = db.Column(db.String(255),nullable=False)
    queryRaw = db.Column(db.Text(),nullable=False)
    apikey_id = db.Column(db.Integer,db.ForeignKey('apikeys.id'))
    tasks = db.relationship("Task",backref="youtube_queries")
    videos = relationship("QueryVideoMM",backref="queries")

    def __init__(self,queryRaw):
        self.queryHash = base64.urlsafe_b64encode(queryRaw)
        self.queryRaw = queryRaw
    def count_videos(self):
        return len(self.videos)
    
    def count_tasks(self):
        return len(self.tasks)
    
    def count_video_meta(self):
        #SELECT count(*) as count FROM meta LEFT OUTER JOIN query_video_mm ON query_video_mm.video_id=meta.id WHERE query_video_mm.youtube_query_id=<query_id>
        print "1"
        r = YoutubeVideoMeta.query()
        print str(r)
        #r = r.outerjoin((query_video_mm,query_video_mm.video_id=meta.id))
        count = 0
            
        return count
    def get_statistics(self):
        return {
                'query': {
                          'videos':len(self.videos),
                          'meta':self.count_video_meta()
                          },
                'all': {
                        'count':0
                        }
        }
    def as_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'queryHash':self.queryHash,
            'queryRaw':json.loads(self.queryRaw),
            'tasks':[task.as_dict() for task in self.tasks]
        }

