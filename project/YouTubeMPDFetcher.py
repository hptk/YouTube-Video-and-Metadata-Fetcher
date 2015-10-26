from RequestBase import RequestBase
import datetime
import urlparse
import urllib
import dateutil.parser
import pprint
import time
import json
import os
import sys
from urllib2 import urlopen, unquote;
from urlparse import parse_qs;
import xmltodict
import pprint
from project import db
import logging
import xml.etree.ElementTree as ET
from project.models import YoutubeQuery, YouTubeVideo, VideoRepresentation
logger = logging.getLogger('tasks')


class YouTubeMPDFetcher(RequestBase):

    def initAdditionalStructures(self):
        pass

    def buildRequestURL(self, workQueueItem):
        return self.url+'?video_id='+workQueueItem

    def initWorkQueue(self):
        queries = YoutubeQuery.query.filter_by(id=self.parameter)
        for video in queries.videos:
            self.putWorkQueueItem(video.video_id)

    def handleRequestSuccess(self,workQueueItem, response):
        video_id = workQueueItem
        video_dbitem = YouTubeVideo.query.filter_by(id=video_id)

        #download manifest
        video_info = parse_qs(unquote(response.read().decode('utf-8')))
        manifest_url = video_info["dashmpd"][0]
        manifest_file = urlopen(manifest_url).read()
        manifest = xmltodict.parse(manifest_file)['MPD']['Period']['AdaptationSet']

        for adaptation in manifest:
            mimeType = adaptation['@mimeType'].split('/')
            representations = adaptation['Representation']
            if not isinstance(representations, list):
                representations = [representations]
            if mimeType[0] == 'audio' and self.get_sound and not got_sound:
                for representation in representations:
                    updating db
                    vr = VideoRepresentation(
                            video_id,
                            adaptation['@mimeType'],
                            representation['@bandwidth'],
                            representation['@codecs']
                            )
                    video_dbitem.representations.append(vr)
                    db.session.add(vr)

            elif mimeType[0] == 'video':
                for representation in representations:
                    updating db
                    vr = VideoRepresentation(
                            video_id,
                            adaptation['@mimeType'],
                            representation['@bandwidth'],
                            representation['@codecs'],
                            representation['@frameRate'],
                            representation['@height'],
                            representation['@width']
                            )
                    video_dbitem.representations.append(vr)
                    db.session.add(vr)

        db.session.add(video_dbitem)
        db.commit()

    def saveResult(self):
        pass

test = YouTubeVideoFetcher("http://www.youtube.com/get_video_info",'hFKacalDPjc',1,1,)
test = YouTubeVideoFetcher("http://www.youtube.com/get_video_info",'a6iTg_FUS74',1,1,)
test.work()
