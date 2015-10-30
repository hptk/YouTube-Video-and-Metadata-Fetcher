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

    result_list = {}

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
        return request

    def initWorkQueue(self):
        video_ids = db.session.query(QueryVideoMM).filter_by(QueryVideoMM.youtube_query_id == self.parameter['video_id'])
        for video_id in video_ids:
            self.putWorkQueueItem([True,
                                   video_id,
                                   '',
                                   self.parameter['get_replies']])

    def handleRequestSuccess(self, workQueueItem, response):
        result = json.load(response)

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
                    self.putWorkQueueItem([False,
                                           workQueueItem[1],
                                           '',
                                           comment_thread['id']])

        for comment_thread in result['items']:
            saveTemporary(workQueueItem, comment_thread)
        print 'Got %d comments for videoId:%s, PNT:%s' % (result['pageInfo']['totalResults'], workQueueItem[1], workQueueItem[2])

    def handleRequestSuccessReplies(self, workQueueItem, result):
        if result.get('nextPageToken'):
            self.putWorkQueueItem([False,
                                   workQueueItem[1],
                                   result['nextPageToken'],
                                   workQueueItem[3]])

        for comment in result['items']:
            self.saveTemporary(workQueueItem, comment)
        print 'Got %d replies for parentId:%s, PNT:%s' % (len(result['items']), workQueueItem[3], workQueueItem[2])

    # Resource is either a comment_thread or a comment
    def saveTemporary(self, workQueueItem, resource):
        comment = resource
        if workQueueItem[0]:
            comment = resource['snippet']['topLevelComment']

        db_comment = {}
        db_comment['video_id'] = str(workQueueItem[1])
        db_comment['thread_id'] = resource['id'] if workQueueItem[0] else workQueueItem[3]
        db_comment['id'] = comment['id']
        db_comment['textDisplay'] = comment['snippet']['textDisplay']
        db_comment['totalReplyCount'] = resource['snippet']['totalReplyCount'] if workQueueItem[0] else -1
        db_comment['authorDisplayName'] = comment['snippet']['authorDisplayName']
        db_comment['authorProfileImageUrl'] = comment['snippet']['authorProfileImageUrl']
        db_comment['authorChannelUrl'] = comment['snippet']['authorChannelUrl']
        db_comment['authorChannelId'] = comment['snippet']['authorChannelId']['value']
        db_comment['authorGooglePlusProfileUrl'] = comment['authorGooglePlusProfileUrl']
        db_comment['likeCount'] = comment['likeCount']
        db_comment['publishedAt'] = comment['publishedAt']
        db_comment['updatedAt'] = comment['updatedAt']

        self.result_list[comment['id']] = db_comment

    def saveResult(self):
        if len(self.result_list) == 0:
            return

        self.updateProgress('SAVING')
        from project.models import YoutubeComment
        from sqlalchemy.ext.compiler import compiles
        from sqlalchemy.sql.expression import Insert
        @compiles(Insert)
        def replace_string(insert, compiler, **kw):
            s = compiler.visit_insert(insert, **kw)
            if 'replace_string' in insert.kwargs:
                return str(s).replace("INSERT",insert.kwargs['replace_string'])
            return s

        logger.info('saving comments')
        db.engine.execute(YoutubeComment.__table__
                                        .insert(replace_string='INSERT OR REPLACE'),
                          self.result_list.values())

if __name__ == '__main__':
    apikey = 'AIzaSyA99dYY8k12G93N9SP5DzmHc95gH5-aIfI'
    test = YouTubeCommentFetcher('https://www.googleapis.com/youtube/v3',
                                 'weTznlEkzfk', 1, 1)
    #pprint(test)
    test.work()

