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

# This class handles both commentThreads and replies.
# The workQueueItem looks different for both tasks
# commentThread:
#   0: True - this is a commentThread
#   1: video id
#   2: pageNextToken
#   3: getReplies (boolean)
#
# reply:
#   0: False - this is a reply
#   1: video id
#   2: pageNextToken
#   3: commentThread id

_COMMENTHREADS_MAXRESULTS = 100
_COMMENTS_MAXRESULTS = 100
apikey=''

class YouTubeCommentFetcher(RequestBase):

    def buildRequestURL(self, workQueueItem):
        request = self.url

        if workQueueItem[0]:
            request += '/commentThreads?videoId=' + workQueueItem[1] +\
                       '&maxResults=' + str(_COMMENTHREADS_MAXRESULTS)
        else:
            request += '/comments?parentId=' + workQueueItem[3] +\
                       '&maxResults=' + str(_COMMENTS_MAXRESULTS)

        if workQueueItem[2] != '':
            request += '&pageToken=' + workQueueItem[2]

        request += '&part=snippet&key=' + apikey
        #print 'WQI: ' + str(workQueueItem)
        #print 'request: ' + request
        return request

    def initWorkQueue(self):
        item = [True, self.parameter, '', True]
        self.putWorkQueueItem(item)

    def handleRequestSuccess(self, workQueueItem, response):
        #pprint(response)
        result = json.load(response)
        #pprint(result)
        '''
        try:
            pprint(result['pageInfo'])
        except:
            pass
        '''

        # No comments were returned
        if not result.get('items'):
            return

        if workQueueItem[0]:
            self.handleRequestSuccessCommentThreads(workQueueItem, result)
        else:
            self.handleRequestSuccessReplies(workQueueItem, result)

    def handleRequestSuccessCommentThreads(self, workQueueItem, result):
        # If the pageNextToken value is set, we can expect there to be more
        # CommentThreads. Spawn a new task to get them.
        if result.get('nextPageToken'):
            self.putWorkQueueItem([True,
                                   workQueueItem[1],
                                   result['nextPageToken'],
                                   workQueueItem[3]])

        # get replies?
        if workQueueItem[3]:
            for comment_thread in result['items']:
                if comment_thread['snippet']['totalReplyCount'] > 0:
                    #print 'Putting workQueueItem for replies to thread:%s' % comment_thread['id']
                    self.putWorkQueueItem([False,
                                           workQueueItem[1],
                                           '',
                                           comment_thread['id']])

            print 'Got %d comments for videoId:%s, PNT:%s' % (result['pageInfo']['totalResults'], workQueueItem[1], workQueueItem[2])

    def handleRequestSuccessReplies(self, workQueueItem, result):
        #print 'handling reply get success!'
        if result.get('nextPageToken'):
            self.putWorkQueueItem([False,
                                   workQueueItem[1],
                                   result['nextPageToken'],
                                   workQueueItem[3]])

        print 'Got %d replies for parentId:%s, PNT:%s' % (len(result['items']), workQueueItem[3], workQueueItem[2])

    def saveResult(self):
        pass

if __name__ == '__main__':
    apikey = 'AIzaSyA99dYY8k12G93N9SP5DzmHc95gH5-aIfI'
    test = YouTubeCommentFetcher('https://www.googleapis.com/youtube/v3',
                                 'weTznlEkzfk', 1, 1)
    #pprint(test)
    test.work()

