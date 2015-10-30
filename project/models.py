# project/models.py

import datetime
from project import db
import json
from sqlalchemy.orm import relationship
import hashlib
import base64
from project.config import BaseConfig
from sqlalchemy.event import listen
from sqlalchemy.pool import Pool
import sqlite3
import math
from sqlalchemy.sql.expression import desc

#http://stackoverflow.com/questions/2298339/standard-deviation-for-sqlite
class StdevFunc:
    """
    For use as an aggregate function in SQLite
    """
    def __init__(self):
        self.M = 0.0
        self.S = 0.0
        self.k = 0

    def step(self, value):
        try:
            # automatically convert text to float, like the rest of SQLite
            val = float(value) # if fails, skips this iteration, which also ignores nulls
            tM = self.M
            self.k += 1
            self.M += ((val - tM) / self.k)
            self.S += ((val - tM) * (val - self.M))
        except:
            pass

    def finalize(self):
        if self.k <= 1: # avoid division by zero
            return none
        else:
            return math.sqrt(self.S / (self.k-1))

def my_on_connect(dbapi_con, connection_record):
    dbapi_con.create_aggregate("stdev", 1, StdevFunc)

listen(Pool, 'connect', my_on_connect)

class VideoCategory(db.Model):

    __tablename__ = "categories"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.VARCHAR(255))
    channel_id = db.Column(db.VARCHAR(15))

    def __init__(self,id,channel_id,title):
        self.id = id
        self.title = title
        self.channel_id = channel_id

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

class YoutubeCommmentThread(db.Model):
    __tablename__ = 'commentThread'

    video_id = db.Column(db.VARCHAR(12), db.ForeignKey('video.id'))

    # Thread_id is either the ID of the commmentThread object, or
    # the parentId of the commment snippet.
    # In the case that these two values are the same,
    # the item is a top-level comment.
    thread_id = db.Column(db.VARCHAR(100));
    id = db.Column(db.VARCHAR(100), primary_key=True);

    # Snippet data
    # There is a field 'textOriginal', but one is only guaranteed
    # access to this if one is the original author (we never are)
    textDisplay = db.Column(db.VARCHAR(1000))
    # Only valid for top-level comments
    totalReplyCount = db.Column(db.Integer)
    authorDisplayName = db.Column(db.VARCHAR(100))
    authorProfileImageUrl = db.Column(db.VARCHAR(100))
    authorChannelUrl = db.Column(db.VARCHAR(100))
    authorChannelId = db.Column(db.VARCHAR(50))
    authorGooglePlusProfileUrl = db.Column(dv.VARCHAR(100))
    likeCount = db.Column(db.Integer)

    publishedAt = db.Column(db.DateTime(timezone=True))
    updatedAt = db.Column(db.DateTime(timezone=True))


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

    #the duration of the video is given as a ISO 8601 time interval
    contentDetails_duration = db.Column(db.VARCHAR(20))
    #the ISO 8601 time interval calculated into seconds
    contentDetails_durationAsSeconds = db.Column(db.Integer)

    contentDetails_dimension = db.Column(db.VARCHAR(2))
    contentDetails_definition = db.Column(db.VARCHAR(2))
    #based on google documentation this field is a string, containing 'true' or 'false', if you want to use boolean instead, you have to manually convert the string into bool
    contentDetails_caption = db.Column(db.String(4))
    contentDetails_licensedContent = db.Column(db.BOOLEAN)

    recordingDetails_location_latitude = db.Column(db.Float(precision='10,6'))
    recordingDetails_location_longitude = db.Column(db.Float(precision='10,6'))
    recordingDetails_location_altitude = db.Column(db.Float(precision='10,6'))
    recordingDetails_recordingDate = db.Column(db.DateTime(timezone=True))

    def getCategoryId(self):
        return self.snippet_category_id

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
        """Returns the amount of videos fetched by this query"""
        return len(self.videos)

    def count_tasks(self):
        """Returns of many tasks where performed for this query"""
        return len(self.tasks)

    def count_video_meta(self):
        """Returns the amount of meta data associated to this query"""
        metas = YoutubeVideoMeta.query.outerjoin((QueryVideoMM, QueryVideoMM.video_id == YoutubeVideoMeta.id)).filter_by(youtube_query_id=self.id)
        count = metas.count()
        return count

    def count_dash(self):
        """Returns the amount of dash representations associated to this query"""
        dashs = VideoRepresentation.query.outerjoin((QueryVideoMM, QueryVideoMM.video_id == VideoRepresentation.video_id)).filter_by(youtube_query_id=self.id)
        count = dashs.count()
        return count

    def get_statistics_dayHistogram(self):
        """Returns a dictonary which contains an aggregation of day=>amount"""
        dates_query = db.session.query(YoutubeVideoMeta,db.func.count().label("count"),db.func.date(YoutubeVideoMeta.snippet_publishedAt).label("date")).outerjoin((QueryVideoMM, QueryVideoMM.video_id == YoutubeVideoMeta.id)).filter_by(youtube_query_id=self.id).group_by(db.func.strftime('%Y',YoutubeVideoMeta.snippet_publishedAt),db.func.strftime('%m',YoutubeVideoMeta.snippet_publishedAt),db.func.strftime('%d',YoutubeVideoMeta.snippet_publishedAt)).order_by(YoutubeVideoMeta.snippet_publishedAt)
        dates = dates_query.all()
        return [{"date":date.date,"count":date.count} for date in dates]

    def getAggregations(self,table,field,forQuery=False):
        """Gets an aggregation of the table.field max,min,avg,sum,stdev
        forQuery: parameter to select the current query, or global
        """
        if forQuery:
            res = db.session.query(table,db.func.stdev(field).label("stdev"),db.func.max(field).label("max"),db.func.min(field).label("min"),db.func.sum(field).label("sum"),db.func.avg(field).label("avg")).filter(field!='').outerjoin((QueryVideoMM, QueryVideoMM.video_id == YoutubeVideoMeta.id)).filter_by(youtube_query_id=self.id)
        else:
            res = db.session.query(table,db.func.stdev(field).label("stdev"),db.func.max(field).label("max"),db.func.min(field).label("min"),db.func.sum(field).label("sum"),db.func.avg(field).label("avg")).filter(field!='')
        row = res.one()
        return row

    def get_statistics_percentile(self,table,field):
        """Gets the 0.1-1.0 percentile of table.field"""
        dict = {}
        for x in xrange(1,11):
            dict[x] = db.session.execute("select statistics_viewCount as percentile from meta order by percentile asc limit 1 OFFSET 19346*"+str(x)+"/10-1").first().percentile


    def get_statistics_assocQuery(self):
        """Performs a backward search to find all queries which have an intersection with the videos, this query has fetched"""
        backrefs = db.session.execute("select first.youtube_query_id as queryid, count(*) as count, second.youtube_query_id as backrefQuery from query_video_mm as first JOIN query_video_mm as second on second.video_id=first.video_id WHERE first.youtube_query_id="+str(self.id)+" AND backrefQuery!="+str(self.id)+" GROUP BY backrefQuery ORDER BY count DESC")
        backrefsQueries = []
        for row in backrefs:
            backrefsQueries.append({'query':YoutubeQuery.query.filter_by(id=row.backrefQuery).first().as_dict(),'count':row.count,'reference':len(self.videos)})
        return backrefsQueries

    def get_statistic_categories(self):
        categories = db.session.execute("SELECT  count(*) AS total, meta.snippet_category_id AS category_id FROM meta LEFT OUTER JOIN query_video_mm ON query_video_mm.video_id = meta.id WHERE query_video_mm.youtube_query_id ="+str(self.id)+" GROUP BY meta.snippet_category_id ORDER BY total DESC LIMIT 10")
        return [{"id":row.category_id,"count":row.total,"name":VideoCategory.query.filter_by(id=row.category_id).first().title} for row in categories]

    def get_statistic_section(self,section):
        """Returns only a section of the complete statistics"""

        if section=="summary":
            return {
                    'data': {
                        'videos':len(self.videos),
                        'meta':self.count_video_meta(),
                        'dash':self.count_dash(),
                    },
                    'global': {
                        'videos':YoutubeVideo.query.count(),
                        'meta':YoutubeVideoMeta.query.count(),
                        }
                    }
        elif section=="publishedAt":
            return self.get_statistics_dayHistogram()

        elif section=="intersection":
            return self.get_statistics_assocQuery()

        elif section=="statistics_likeCount" or section=="statistics_dislikeCount" or section=="statistics_commentCount" or section=="statistics_viewCount":
            table = YoutubeVideoMeta
            if section=="statistics_likeCount":
                field = YoutubeVideoMeta.statistics_likeCount
            elif section=="statistics_dislikeCount":
                field = YoutubeVideoMeta.statistics_dislikeCount
            elif section=="statistics_commentCount":
                field = YoutubeVideoMeta.statistics_commentCount
            elif section=="statistics_viewCount":
                field = YoutubeVideoMeta.statistics_viewCount

            globalStat = self.getAggregations(table,field,forQuery=False)
            queryStat = self.getAggregations(table,field,forQuery=True)
            #queryPercentile = self.get_statistics_percentile(table,field)
            return {
                    section:{
                             'data':{
                                      'max':queryStat.max,
                                      'min':queryStat.min,
                                      'sum':queryStat.sum,
                                      'avg':queryStat.avg,
                                      'stdev':queryStat.stdev
                                      },
                             #'percentile': queryPercentile,
                             'global':{
                                       'max':globalStat.max,
                                       'min':globalStat.min,
                                       'sum':globalStat.sum,
                                       'avg':globalStat.avg,
                                       'stdev':globalStat.stdev
                              }
                             }
            }
        elif section=="category":
            categories = self.get_statistic_categories()
            return categories

    def as_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'queryHash':self.queryHash,
            'queryRaw':json.loads(self.queryRaw),
            'tasks':[task.as_dict() for task in self.tasks]
        }

