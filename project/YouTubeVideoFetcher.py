from RequestBase import RequestBase
from urllib2 import urlopen, unquote;
from urlparse import parse_qs;
import urlparse
import urllib
import time
import os
import sys
import xmltodict
import logging
import random
logger = logging.getLogger('tasks')
from project import db
from project.models import QueryVideoMM

# TODO:
# parameters:
#   this file requires: (not yet tested or fixed)
#       'id', the id of the query to fetch the videos of,
#       workQueueItem should be as follows:
#           0: video id
#           1: the height (resolution) preffered to be dl'ed (e.g. 1080, 720)
#           2: get sound? Boolean value

class YouTubeVideoFetcher(RequestBase):
    video_ids = []
    dl_path = ''
    get_sound = False

    def initAdditionalStructures(self):
        dir = os.path.dirname(__file__)
        self.dl_path = os.path.join(dir, '../downloads/')
        
        

    def buildRequestURL(self, workQueueItem):
        return self.url + '?video_id=' + workQueueItem[0]

    def initWorkQueue(self):
        
        #seeded random select from DB
        if self.parameter['method']=='random':
            random.seed(self.parameter['amount'])
            seed = random.random() 
            video_ids = db.session.execute('SELECT id as video_id from video JOIN query_video_mm on query_video_mm.video_id=video.id WHERE youtube_query_id='+str(self.parameter["queryId"])+' ORDER by (substr((uid)*'+str(seed)+',length(uid)+2)) LIMIT '+str(self.parameter["amount"]))
        else:
            #select all videos from the db
            video_ids = db.session.query(QueryVideoMM).filter_by(youtube_query_id=self.parameter['queryId'])
            
        for video in video_ids:
            self.putWorkQueueItem([video.video_id,
                                    self.parameter['resolution'],
                                    self.parameter['sound']])

    def handleRequestSuccess(self,workQueueItem, response):
        got_video = False
        got_sound = False
        video_id = workQueueItem[0]
        CHUNK = 16 * 1024
        path = self.dl_path
        if workQueueItem[2]:
            self.get_sound = True

        #download manifest
        video_info = parse_qs(unquote(response.read().decode('utf-8')))
        try:
            manifest_url = video_info['dashmpd'][0]
            manifest_file = urlopen(manifest_url).read()
            manifest = xmltodict.parse(manifest_file)['MPD']['Period']['AdaptationSet']
        except:
            if 'reason' in video_info:
                logger.info('MPD fething failed for ' + str(video_id) + ' : ' + video_info['reason'][0])
            elif 'errorcode' in video_info:
                logger.info('MPD fething failed for ' + str(video_id)+' : errorcode ' + video_info['errorcode'][0])
            elif 'errordetail' in video_info:
                logger.info('MPD fething failed for ' + str(video_id)+' : errordetail ' + video_info['errordetail'][0])
            elif 'status' in video_info:
                logger.info('MPD fething failed for ' + str(video_id)+' : status ' + video_info['status'][0])
            else:
                logger.info('MPD fething failed for ' + str(video_id)+' : unknown error')
            return
        
        for adaptation in manifest:
            mimeType = adaptation['@mimeType'].split('/')
            if mimeType[0] == 'audio' and self.get_sound and not got_sound:
                filename = path + '/sound/' + video_id + '.' + ('m4a' if mimeType[1] == 'mp4' else mimeType[1])
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                
                already_downloaded_sound = os.path.isfile(filename)
                #only download if file is not already downloaded
                if not already_downloaded_sound:
                    with open(filename, "w") as f:
                        representation = adaptation['Representation']
                        if isinstance(representation, list):
                            representation = representation[0] #select first available sound
                        url = representation['BaseURL']['#text']
                        filesize = int(representation['BaseURL']['@yt:contentLength'])
                        response = urllib.urlopen(url)
                        dl = 0
                        logger.info('Downloading sound! > ' + video_id + ' ' + mimeType[1])
                        while True and dl<filesize:
                            done = int(50 * dl / filesize)
                            dl += CHUNK
                            #sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                            #sys.stdout.flush()
                            chunk = response.read(CHUNK)
                            if not chunk: break
                            f.write(chunk)
                    #print 'DONE!'
                got_sound = True

            #download video file, quality as specified
            elif mimeType[0] == 'video':
                filename = path + '/video/' + video_id
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                representations = adaptation['Representation']
                if not isinstance(representations, list):
                    representations = [representations]
                for representation in representations:
                    last_representation = representation
                    if not str(representation['@height']) == str(workQueueItem[1]):
                        continue
                    else:
                        break
                filename += '.' + last_representation['@height'] + '.' + ('m4v' if mimeType[1] == 'mp4' else mimeType[1])
                #only download if file is not already downloaded
                already_downloaded_representation = os.path.isfile(filename)
                if not already_downloaded_representation:
                    with open(filename, "w") as f:
                        url = last_representation['BaseURL']['#text']
                        response = urllib.urlopen(url)
                        dl = 0
                        filesize = int(last_representation['BaseURL']['@yt:contentLength'])
                        logger.info('Downloading video! > ' + video_id + ' ' + last_representation['@height'] + 'p' + "size: "+str(filesize))
                        while True and dl<filesize:
                            done = int(50 * dl / filesize)
                            dl += CHUNK
                            #sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                            #sys.stdout.flush()
                            chunk = response.read(CHUNK)
                            if not chunk: break
                            f.write(chunk)
                        #print 'DONE!'
                got_video = True

            if got_video and (got_sound or (not self.get_sound and not got_sound)):
                #add to resultList for nice progress bar in the UI
                self.resultList[str(video_id)]=None
                break

    def saveResult(self):
        pass

