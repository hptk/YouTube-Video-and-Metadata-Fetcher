from RequestBase import RequestBase
import datetime
import json
import urlparse
import urllib
import dateutil.parser
import pprint 
import time
from project import db
import logging
logger = logging.getLogger('tasks')
class YouTubeIDFetcher(RequestBase):
         
    def initAdditionalStructures(self):
        self.query = json.loads(self.parameter['queryRaw'])
        #add default parameter to the list / override
        self.query['part'] = "snippet"
        self.query['maxResults'] = "50"
        self.query['order'] = "date"
        self.query['type'] = "video"
            
        #save initial timeframe into variables and delete them from the parameter list, copy value
        self.publishedBefore = dateutil.parser.parse(self.query['publishedBefore'])
        self.publishedAfter = dateutil.parser.parse(self.query['publishedAfter'])
        del self.query['publishedBefore']
        del self.query['publishedAfter']
        
        url_parts = list(urlparse.urlparse(self.url))
        parameter = dict(urlparse.parse_qsl(url_parts[4]))
        parameter.update(self.query)
        url_parts[4] = urllib.urlencode(parameter)
        self.defaultURL = urlparse.urlunparse(url_parts)
           
    def calculateTimeframe(self,publishedBefore,frame):
        return publishedBefore - datetime.timedelta(seconds=frame)
    
    def formatDate(self,date):
        return date.strftime('%FT%TZ')
    
    def buildRequestURL(self, workQueueItem):
        publishedAfter = workQueueItem[0]
        publishedBefore = workQueueItem[1] 
        return self.defaultURL+"&publishedAfter="+self.formatDate(publishedAfter)+"&publishedBefore="+self.formatDate(publishedBefore);
    
    def handleRequestSuccess(self,workQueueItem, result):
        if "items" in result:
            req_results = len(result['items'])
            #do something with the data
            for item in result['items']:
                self.resultList[str(item['id']['videoId'])]=None
                
            publishedAfter = workQueueItem[0]
            publishedBefore = workQueueItem[1]
            secondsTimeSpan = int((publishedBefore-publishedAfter).total_seconds())
            #slice the timeframe if has more pages and more results than 50 and the timespan is bigger than 1 (maybe there are more than 50 videos per second and it will result in a loop)
            if "nextPageToken" in result and req_results==50 and secondsTimeSpan > 1:
                midDate = publishedAfter+(publishedBefore-publishedAfter)/2
                #add new timeframes to queue
                self.putWorkQueueItem((publishedAfter,midDate-datetime.timedelta(seconds=1)))
                self.putWorkQueueItem((midDate,publishedBefore)) 
    
    def initWorkQueue(self):
        self.totalFrame = int((self.publishedBefore-self.publishedAfter).total_seconds())
        self.secondsPerFrame = int(self.totalFrame/(self.numberHTTPClients))
        self.initFrames = int(self.totalFrame/self.secondsPerFrame)
        
        tempTime = self.publishedBefore
        for x in xrange(0,self.initFrames):
            tempTimeBefore = self.calculateTimeframe(tempTime,x*self.secondsPerFrame)
            tempTimeAfter = self.calculateTimeframe(tempTimeBefore,self.secondsPerFrame)
            tempTime = self.calculateTimeframe(tempTime,1)
            self.putWorkQueueItem((tempTimeAfter,tempTimeBefore))
    
    def saveResult(self):
        if len(self.resultList) > 0:
            self.updateProgress('SAVING')
            from project.models import YoutubeVideo, QueryVideoMM
            #http://docs.sqlalchemy.org/en/rel_0_8/faq.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow
            #used described pattern to have better performance: sqlalchemy core insert
            
            
            #fix duplicate key problem: http://stackoverflow.com/questions/6611563/sqlalchemy-on-duplicate-key-update
            #http://stackoverflow.com/questions/418898/sqlite-upsert-not-insert-or-replace/4330694#4330694
            from sqlalchemy.ext.compiler import compiles 
            from sqlalchemy.sql.expression import Insert
            @compiles(Insert)
            def replace_string(insert, compiler, **kw):
                s = compiler.visit_insert(insert, **kw)
                if 'replace_string' in insert.kwargs:
                    return str(s).replace("INSERT",insert.kwargs['replace_string'])
                return s
            
            t0 = time.time()
            logger.info("save video ids")
            #http://docs.sqlalchemy.org/en/rel_0_9/core/connections.html?highlight=engine#sqlalchemy.engine.Connection.execute
            db.engine.execute(YoutubeVideo.__table__.insert(replace_string = 'INSERT OR REPLACE'),
                   [{"id": videoID} for videoID in self.resultList]
                   )
            logger.info("Total time for " + str(len(self.resultList)) +" records " + str(time.time() - t0) + " secs")
            
            logger.info("save query video association")
            db.engine.execute(QueryVideoMM.__table__.insert(replace_string = 'INSERT OR REPLACE'),
                   [{"youtube_query_id":self.parameter['queryId'],"video_id": videoID} for videoID in self.resultList]
                   )
            logger.info("Total time for " + str(len(self.resultList)) +" records " + str(time.time() - t0) + " secs")

            
##how to use it
#query= {}
#query['publishedBefore'] = "2015-09-0T22:00:00Z"
#query['publishedAfter'] = "2015-09-01T22:00:00Z"
#query['key'] = 'AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8'
#json_query = json.dumps(query)
#test = YouTubeIDFetcher("https://www.googleapis.com/youtube/v3/search",json_query,50,50)  
#pprint.pprint(test.work())

