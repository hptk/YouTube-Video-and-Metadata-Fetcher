from RequestAbstraction import RequestAbstraction
from itertools import islice 
from project import db
import logging
import time
import pprint
import json
import dateutil.parser
from datetime import datetime
logger = logging.getLogger('tasks')
class YouTubeMetaFetcher(RequestAbstraction):
    
    def chunkHelper(self,data,SIZE=50):
        it=iter(data)
        for i in xrange(0,len(data),SIZE):
            yield {k for k in islice(it, SIZE)}
       
    def initWorkQueue(self):
        """initialize the working queue, selecting all video ids for the given query id"""
        #nice to have: only select which do not have meta data yet in order 
        
        #fetch all rows
        videoIDRows = db.engine.execute('select video_id from query_video_mm where youtube_query_id='+str(self.parameter))
        #convert to list of dicts
        videoIDs = {}
        for video in videoIDRows:
            videoIDs[video['video_id'] ] = video['video_id'] 
        logger.info("fetching meta data for "+str(len(videoIDs))+" videos")
        
        for videoTuple in self.chunkHelper(videoIDs, 50):
            self.putWorkQueueItem(videoTuple)          
        logger.info("resulting in "+str(self.workQueue.qsize())+" requests to make")
          
    def buildRequestURL(self, workQueueItem):
        #because we have put 50 videoIDs per queueItem, we have to implode it like "id1,id2,id3,id4,...,id49,id50"
        videoIDs = ','.join(workQueueItem)
        return self.url+"?part=snippet,contentDetails,liveStreamingDetails,recordingDetails,statistics,status,topicDetails&id="+videoIDs+"&key=AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"
    
    
        
    def handleRequestSuccess(self,workQueueItem, result):
        if "items" in result:
            for item in result['items']:
                #database maping
                self.resultList[item['id']]= {}
                self.resultList[item['id']]["id"] = item['id']
                        
                #snippet
                self.resultList[item['id']]["snippet_publishedAt"] = dateutil.parser.parse(item['snippet']['publishedAt'])
                self.resultList[item['id']]["snippet_channel_id"] = item['snippet']['channelId']
                self.resultList[item['id']]["snippet_title"] = item['snippet']['title']
                self.resultList[item['id']]["snippet_description"] = item['snippet']['description']
                self.resultList[item['id']]["snippet_channel_title"] = item['snippet']['channelTitle']
                self.resultList[item['id']]["snippet_category_id"] = item['snippet']['categoryId']
                self.resultList[item['id']]["snippet_liveBroadcastContent"] = item['snippet']['liveBroadcastContent']
                if 'tags' in item['snippet']:
                    self.resultList[item['id']]["snippet_tags"] = json.dumps(item['snippet']['tags'])
                else:
                    self.resultList[item['id']]["snippet_tags"] = ''
                    
                #contentDetails
                self.resultList[item['id']]["contentDetails_duration"] = item['contentDetails']['duration']
                self.resultList[item['id']]["contentDetails_dimension"] = item['contentDetails']['dimension']
                self.resultList[item['id']]["contentDetails_definition"] = item['contentDetails']['definition']
                self.resultList[item['id']]["contentDetails_caption"] = item['contentDetails']['caption']
                self.resultList[item['id']]["contentDetails_licensedContent"] = item['contentDetails']['licensedContent']
                
                #status
                self.resultList[item['id']]["status_uploadStatus"] = item['status']['uploadStatus']
                self.resultList[item['id']]["status_privacyStatus"] = item['status']['privacyStatus']
                self.resultList[item['id']]["status_license"] = item['status']['license']
                self.resultList[item['id']]["status_embeddable"] = item['status']['embeddable']
                self.resultList[item['id']]["status_publicStatsViewable"] = item['status']['publicStatsViewable']
                
                #statistics
                self.resultList[item['id']]["statistics_viewCount"] = int(item['statistics']['viewCount'])
                if "likeCount" in item['statistics']:
                    self.resultList[item['id']]["statistics_likeCount"] = int(item['statistics']['likeCount'])
                else:
                    self.resultList[item['id']]["statistics_likeCount"] = ''
                
                if "dislikeCount" in item['statistics']:
                    self.resultList[item['id']]["statistics_dislikeCount"] = int(item['statistics']['dislikeCount'])
                else:
                    self.resultList[item['id']]["statistics_dislikeCount"] = ''
                    
                self.resultList[item['id']]["statistics_favoriteCount"] = int(item['statistics']['favoriteCount'])
                self.resultList[item['id']]["statistics_commentCount"] = int(item['statistics']['commentCount'])
                
                #recordingDetails
                if 'recordingDetails' in item:
                    
                    if 'recordingDate' in item['recordingDetails']:
                        self.resultList[item['id']]["recordingDetails_recordingDate"] = dateutil.parser.parse(item['recordingDetails']['recordingDate'])
                    else:
                        #add epoch to the field if value not exists, because SQLite DateTime type only accepts Python datetime and date objects as input
                        self.resultList[item['id']]["recordingDetails_recordingDate"] = datetime.utcfromtimestamp(0)
                    if "location" in item['recordingDetails']:
                        if 'latitude' in item['recordingDetails']['location']:
                            self.resultList[item['id']]["recordingDetails_location_latitude"] = item['recordingDetails']['location']['latitude']
                        else:
                            self.resultList[item['id']]["recordingDetails_location_latitude"] = 0
                        if 'longitude' in item['recordingDetails']['location']:
                            self.resultList[item['id']]["recordingDetails_location_longitude"] = item['recordingDetails']['location']['longitude']
                        else:
                            self.resultList[item['id']]["recordingDetails_location_longitude"] = 0
                        if 'altitude' in item['recordingDetails']['location']:
                            self.resultList[item['id']]["recordingDetails_location_altitude"] = item['recordingDetails']['location']['altitude']
                        else:
                            self.resultList[item['id']]["recordingDetails_location_altitude"] = 0
                    else:
                        self.resultList[item['id']]["recordingDetails_location_latitude"] = 0
                        self.resultList[item['id']]["recordingDetails_location_longitude"] = 0
                        self.resultList[item['id']]["recordingDetails_location_altitude"] = 0
                else:
                    #add epoch to the field if value not exists, because SQLite DateTime type only accepts Python datetime and date objects as input
                    self.resultList[item['id']]["recordingDetails_recordingDate"] = datetime.utcfromtimestamp(0)
                    self.resultList[item['id']]["recordingDetails_location_latitude"] = 0
                    self.resultList[item['id']]["recordingDetails_location_longitude"] = 0
                    self.resultList[item['id']]["recordingDetails_location_altitude"] = 0
                    
    def saveResult(self):
        
        #
        #
        #
        # maybe save the result after each request (50 meta data sets), because the dictonary eats a lot of ram if there are a lot of videos
        # up to 2.3 GB for 244856 videos in a single task
        #
        #
        
        if len(self.resultList) > 0:
            self.updateProgress('SAVING')
            from project.models import YoutubeVideoMeta
            from sqlalchemy.ext.compiler import compiles 
            from sqlalchemy.sql.expression import Insert
            @compiles(Insert)
            def replace_string(insert, compiler, **kw):
                s = compiler.visit_insert(insert, **kw)
                if 'replace_string' in insert.kwargs:
                    return str(s).replace("INSERT",insert.kwargs['replace_string'])
                return s
            
            t0 = time.time()
            logger.info("save video meta")
            #http://docs.sqlalchemy.org/en/rel_0_9/core/connections.html?highlight=engine#sqlalchemy.engine.Connection.execute
            db.engine.execute(YoutubeVideoMeta.__table__.insert(replace_string = 'INSERT OR REPLACE'),
                   [value for key,value in self.resultList.iteritems()]
                   )
            logger.info("Total time for " + str(len(self.resultList)) +" records " + str(time.time() - t0) + " secs")
            

    