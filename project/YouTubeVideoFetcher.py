from RequestBase import RequestBase
import datetime
import urlparse
import urllib
import dateutil.parser
import pprint
import time
import json
import os
from urllib2 import urlopen, unquote;
from urlparse import parse_qs;
import xmltodict
import pprint
#from project import db
import logging
import xml.etree.ElementTree as ET
#from project.models import YoutubeQuery
logger = logging.getLogger('tasks')

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
        return self.url+'?video_id='+workQueueItem[0]

    def initWorkQueue(self):
        #queries = YoutubeQuery.query.filter_by(id=id)
        #for video in queries.videos:
        #    self.video_ids += video.video_id
        item = {}
        item[0] = self.parameter
        item[1] = 720
        item[2] = False
        self.putWorkQueueItem(item)

    def handleRequestSuccess(self,workQueueItem, response):

        #download manifest
        video_info = parse_qs(unquote(response.read().decode('utf-8')))
        manifest_url = video_info["dashmpd"][0]
        manifest_file = urlopen(manifest_url).read()
        manifest = xmltodict.parse(manifest_file)['MPD']['Period']['AdaptationSet']

        got_video = False
        got_sound = False
        CHUNK = 16 * 1024
        if workQueueItem[2]:
            self.get_sound = True
        for adaptationSet in manifest:
            mimeType = adaptationSet['@mimeType'].split('/')
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
                print 'got sound!'

            #download video file, quality as specified or if no match, get best
            #format should be mp4
            elif mimeType[0] == 'video':
                filename = self.dl_path+workQueueItem[0]+'.'+('m4v' if mimeType[1] == 'mp4' else mimeType[1])
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                with open(filename, "w") as f:
                    last_representation = {}
                    for representation in adaptationSet['Representation']:
                        last_representation = representation
                        if not representation['@height'] == workQueueItem[1]:
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
            if got_video and (got_sound or (not self.get_sound and not got_sound)):
                break

    def saveResult(self):
        pass

test = YouTubeVideoFetcher("http://www.youtube.com/get_video_info",'50KDpBMnADA',1,1,)
pprint.pprint(test.work())
