from RequestBase import RequestBase
from itertools import islice
from project import db
import logging
import time
import pprint
import json
import re
#import dateutil
from dateutil.parser import parse as dateParse
from datetime import datetime
from project.models import YoutubeVideoMeta
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert
logger = logging.getLogger('tasks')
class YouTubeMetaFetcher(RequestBase):

    def chunkHelper(self,data,SIZE=50):
        """Chunks a given dictonary in smaller dictionaries of the size SIZE"""
        it=iter(data)
        for i in xrange(0,len(data),SIZE):
            yield {k for k in islice(it, SIZE)}

    def ISO8601durationToSeconds(self,duration):
        """Converts a ISO 8601 interval like PT15M33S into seconds"""
        match = re.match('P(?:(?:([0-9,.]*)Y)?(?:([0-9,.]*)M)?(?:([0-9,.]*)D)?(?:T(?:([0-9,.]*)H)?(?:([0-9,.]*)M)?(?:([0-9,.]*)S)?)?|([0-9,.]*)W)', duration).groups()
        years = self.parseInt(match[0]) if match[0] else 0
        months = self.parseInt(match[1]) if match[1] else 0
        days = self.parseInt(match[2]) if match[2] else 0
        hours = self.parseInt(match[3]) if match[3] else 0
        minutes = self.parseInt(match[4]) if match[4] else 0
        seconds = self.parseInt(match[5]) if match[5] else 0
        return years *31536000 + months * 2628000 + days*86400 + hours * 3600 + minutes * 60 + seconds

    def parseInt(self,string):
        """Converts a string into integer"""
        return int(string)

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



    def handleRequestSuccess(self,workQueueItem, response):
        result = json.load(response)
        if "items" in result:
            for item in result['items']:
                #database mapping
                db_meta = {'id': item['id']}

                #snippet
                snippet = item['snippet']
                db_meta['snippet_publishedAt'] = dateParse(snippet['publishedAt'])
                db_meta['snippet_channel_id'] = snippet['channelId']
                db_meta['snippet_title'] = snippet['title']
                db_meta['snippet_description'] = snippet['description']
                db_meta['snippet_channel_title'] = snippet['channelTitle']
                db_meta['snippet_category_id'] = snippet['categoryId']
                db_meta['snippet_liveBroadcastContent'] = snippet['liveBroadcastContent']
                db_meta['snippet_tags'] = json.dumps(snippet['tags']) if snippet.get('tags') else ''

                #contentDetails
                c_details = item['contentDetails']
                db_meta['contentDetails_duration'] = c_details['duration']
                db_meta['contentDetails_durationAsSeconds'] = self.ISO8601durationToSeconds(c_details['duration'])
                db_meta['contentDetails_dimension'] = c_details['dimension']
                db_meta['contentDetails_definition'] = c_details['definition']
                db_meta['contentDetails_caption'] = c_details['caption']
                db_meta['contentDetails_licensedContent'] = c_details['licensedContent']

                #status
                status = item['status']
                db_meta['status_uploadStatus'] = status['uploadStatus']
                db_meta['status_privacyStatus'] = status['privacyStatus']
                db_meta['status_license'] = status['license']
                db_meta['status_embeddable'] = status['embeddable']
                db_meta['status_publicStatsViewable'] = status['publicStatsViewable']

                #statistics
                #TODO: Cast to int needed?
                stats = item['statistics']
                db_meta['statistics_viewCount'] = stats['viewCount']
                db_meta['statistics_likeCount'] = stats.get('likeCount') or ''
                db_meta['statistics_dislikeCount'] = stats.get('dislikeCount') or ''
                db_meta['statistics_favoriteCount'] = stats['favoriteCount']
                db_meta['statistics_commentCount'] = stats['commentCount']

                #recordingDetails
                def deep_get(item, *attrs):
                    ''' Get item, or return fallback value from nested dicts '''
                    if item and not isinstance(item, dict):
                        return item
                    if not item:
                        return None
                    return deep_get(item.get(attrs[0]), *attrs[1:])

                if deep_get(item, 'recordingDetails', 'recordingDate'):
                    db_meta['recordingDetails_recordingDate'] = dateParse(deep_get(item, 'recordingDetails', 'recordingDate'))
                else:
                    db_meta['recordingDetails_recordingDate'] = datetime.utcfromtimestamp(0)

                db_meta['recordingDetails_location_latitude'] = deep_get(item, 'recordingDetails', 'location', 'latitude') or 0
                db_meta['recordingDetails_location_longitude'] = deep_get(item, 'recordingDetails', 'location', 'longitude') or 0
                db_meta['recordingDetails_location_altitude'] = deep_get(item, 'recordingDetails', 'location', 'altitude') or 0

                self.resultList[item['id']] = db_meta

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
                   self.resultList.values()
                   )
            logger.info("Total time for " + str(len(self.resultList)) +" records " + str(time.time() - t0) + " secs")



