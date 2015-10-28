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
#           0: video id
#           1: pageNextToken
#           2: getReplies (boolean)

_COMMENTHREADS_MAXRESULTS = 100
_COMMENTS_MAXRESULTS = 100
apikey=''

class YouTubeCommentFetcher(RequestBase):

    def buildRequestURL(self, workQueueItem):
        request = self.url + '?videoId=' + workQueueItem[0] +\
                             '&part=snippet' +\
                             '&maxResults=' + str(_COMMENTHREADS_MAXRESULTS) +\
                             '&key=' + apikey
        if workQueueItem[1] != '':
            request += '&pageNextToken=' + workQueueItem[1]
        return request

    def initWorkQueue(self):
        item = [self.parameter, '', False]
        self.putWorkQueueItem(item)

    def handleRequestSuccess(self,workQueueItem, response):
        result = json.load(response)

        # No commentThreads were returned
        if not result['items']:
            return

        # If we fetched the maximum number of results per page and the
        # pageNextToken value is set, we can expect there to be more
        # CommentThreads. Spawn a new task to get them.
        if result['pageInfo']['totalResults'] ==\
                result['pageInfo']['resultsPerPage'] and\
                result.get('nextPageToken'):
            self.putWorkQueueItem([workQueueItem[0],
                                   result['nextPageToken'],
                                   workQueueItem[2]])

        pprint(result)
        #print 'Got %d results for videoId:%s, PNT:%s' % (result['pageInfo']['totalResults'], workQueueItem[0], workQueueItem[1])

    def saveResult(self):
        pass

if __name__ == '__main__':
    #with open('dash_wallenburg_youtube_apikey_1') as f:
    #    apikey = f.read().rstrip()
    apikey = 'AIzaSyA99dYY8k12G93N9SP5DzmHc95gH5-aIfI'
    test = YouTubeCommentFetcher('https://www.googleapis.com/youtube/v3/commentThreads',
                                 'YiVhFgN7I_M', 1, 1)
    #pprint(test)
    test.work()

