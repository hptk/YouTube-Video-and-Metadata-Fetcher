from RequestAbstraction import RequestAbstraction
import pprint
from itertools import islice 
from project import db
import logging
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
                self.resultList[str(item['id'])]=1
                print item['snippet']['title']
