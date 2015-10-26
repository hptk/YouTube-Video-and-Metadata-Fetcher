#!/usr/bin/env python2.7

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
from pprint import pprint
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
#           0: commentThread id
#           1: get replies? (boolean)

_COMMENTHREAD_MAXRESULTS = 100
apikey=''

class YouTubeCommentFetcher(RequestBase):

    def buildRequestURL(self, workQueueItem):
        request = self.url + '?videoId=' + workQueueItem[0] +\
                            '&part=snippet' +\
                            '&maxResults=' + str(_COMMENTHREAD_MAXRESULTS) +\
                            '&key=' + apikey
        pprint(request)
        return request

    def initWorkQueue(self):
        item = [self.parameter, False]
        self.putWorkQueueItem(item)

    def handleRequestSuccess(self,workQueueItem, response):
        result = json.loads(response)
        pprint(result)
        pass

    def saveResult(self):
        pass

if __name__ == '__main__':
    with open('dash_wallenburg_youtube_apikey_1') as f:
        apikey = f.read().rstrip()

    test = YouTubeCommentFetcher('https://www.googleapis.com/youtube/v3/commentThreads',
                                 'YiVhFgN7I_M', 1, 1)
    #pprint(test)
    test.work()

