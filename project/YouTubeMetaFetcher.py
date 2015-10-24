from RequestAbstraction import RequestAbstraction
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
                #database maping
                self.resultList[item['id']]= {}
                self.resultList[item['id']]["id"] = item['id']
                self.resultList[item['id']]["category_id"] = item['categoryId']
                #snippet
                self.resultList[item['id']]["publishedAt"] = item['snippet']['publishedAt']
                self.resultList[item['id']]["channel_id"] = item['snippet']['channelId']
                self.resultList[item['id']]["title"] = item['snippet']['title']
                self.resultList[item['id']]["description"] = item['snippet']['description']
                self.resultList[item['id']]["channel_title"] = item['snippet']['channelTitle']
                self.resultList[item['id']]["tags"] = json.dumps(item['snippet']['tags'])
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
                self.resultList[item['id']]["statistics_viewCount"] = item['statistics']['viewCount']
                self.resultList[item['id']]["statistics_likeCount"] = item['statistics']['likeCount']
                self.resultList[item['id']]["statistics_dislikeCount"] = item['statistics']['dislikeCount']
                self.resultList[item['id']]["statistics_favoriteCount"] = item['statistics']['favoriteCount']
                self.resultList[item['id']]["statistics_commentCount"] = item['statistics']['commentCount']