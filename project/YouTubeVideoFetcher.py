from RequestAbstraction import RequestAbstraction
import datetime
import json
import urlparse
import urllib
import dateutil.parser
import pprint
import time
import os
from project import db
import logging
from project.models import YoutubeQuery
logger = logging.getLogger('tasks')

# TODO:
# parameters:
#   this file requires: (not yet tested or fixed)
#       'id', the id of the query to fetch the videos of,
#       workQueueItem should be as follows:
#           0: video id
#           1: the height (resolution) preffered to be dl'ed (e.g. 1080, 720)
#           2: get sound? Boolean value

class YouTubeVideoFetcher(RequestAbstraction):
    video_ids = []
    dl_path = ''
    get_sound = False

    def initAdditionalStructures(self):
        self.defaultURL = 'http://www.youtube.com/get_video_info?'
        dir = os.path.dirname(__file__)
        self.dl_path = os.path.join(dir, '../downloads/')

    def buildRequestURL(self, workQueueItem):
        return self.defaultURL+'&video_id='+workQueueItem[0]

    def initWorkQueue(self):
        queries = YoutubeQuery.query.filter_by(id=id)
        for video in queries.videos:
            self.video_ids += video.video_id

    def handleRequestSuccess(self,workQueueItem, result):
        manifest = xmltodict.parse(result)['MPD']['Period']
        got_video = False
        got_sound = False
        CHUNK = 16 * 1024
        if workQueueItem[2]:
            self.get_sound = True
        for adaptationSet in manifest:
            mimeType = (str)adaptationSet['@mimeType'].split('/')

            # Downloading sound, for now first quality listed (should be mp4)
            if mimeType[0] == 'audio' and self.get_sound:
                filename = self.dl_path+workQueueItem[0]+'.'+('m4a' if mimeType[1] == 'mp4' else mimeType[1]+'s')
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                with open(filename, "w") as f:
                    url = adaptationSet['Representation']['BaseURL']['#text']
                    response = urllib.urlopen(url)
                    while True:
                        chunk = response.read(CHUNK)
                        if not chunk: break
                        f.write(chunk)
                got_sound = True

            #download video file, quality as specified or if no match, get best
            #format should be mp4
            elif mimeType[0] == 'video':
                filename = self.dl_path+workQueueItem[0]+'.'+('m4v' if mimeType[1] == 'mp4' else mimeType[1])
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                with open(filename, "w") as f:
                    last_representation = {}
                    for representation in adaptationSet:
                        if not representation['@height'] == workQueueItem[1]:
                            last_representation = representation
                            continue
                        else:
                            break
                    url = last_representation['BaseURL']['#text']
                    response = urllib.urlopen(url)
                    while True:
                        chunk = response.read(CHUNK)
                        if not chunk: break
                        f.write(chunk)
                got_video = True
            if got_video and got_sound:
                break

    def saveResult(self):
        pass

