import time
import json
import os
import sys
import xmltodict
import logging
import xml.etree.ElementTree as ET
from RequestBase import RequestBase
from urllib2 import urlopen, unquote;
from urlparse import parse_qs;
from project import db
from project.models import QueryVideoMM
logger = logging.getLogger('tasks')
import pprint

class YouTubeMPDFetcher(RequestBase):

    def initAdditionalStructures(self):
        pass

    def buildRequestURL(self, workQueueItem):
        return self.url+'?video_id='+workQueueItem

    def initWorkQueue(self):
        videoIDs = db.session.query(QueryVideoMM).filter_by(youtube_query_id=self.parameter).all()
        for video in videoIDs:
            self.putWorkQueueItem(video.video_id)

    def handleRequestSuccess(self,workQueueItem, response):
        video_id = workQueueItem

        #download manifest
        video_info = parse_qs(unquote(response.read().decode('utf-8')))
        try:
            manifest_url = video_info['dashmpd'][0]
            manifest_file = urlopen(manifest_url).read()
            manifest = xmltodict.parse(manifest_file)['MPD']['Period']['AdaptationSet']
        except:
            if 'reason' in video_info:
                logger.info('MPD fething failed for '+str(video_id)+' : '+video_info['reason'][0])
            elif 'errorcode' in video_info:
                logger.info('MPD fething failed for '+str(video_id)+' : errorcode '+video_info['errorcode'][0])
            elif 'errordetail' in video_info:
                logger.info('MPD fething failed for '+str(video_id)+' : errordetail '+video_info['errordetail'][0])
            elif 'status' in video_info:
                logger.info('MPD fething failed for '+str(video_id)+' : status '+video_info['status'][0]+' (possibly live stream)')
            else:
                logger.info('MPD fething failed for '+str(video_id)+' : unknown error')
            return

        for adaptation in manifest:
            mimeType = adaptation['@mimeType'].split('/')
            representations = adaptation['Representation']
            if not isinstance(representations, list):
                representations = [representations]
            if mimeType[0] == 'audio':
                for representation in representations:
                    uniqueKey = str(video_id)+str(representation['@id'])
                    self.resultList[uniqueKey]= {}
                    self.resultList[uniqueKey]['video_id'] = video_id
                    self.resultList[uniqueKey]['mimeType'] = adaptation['@mimeType'] if '@mimeType' in adaptation else ''
                    self.resultList[uniqueKey]['bandwidth'] = representation['@bandwidth'] if '@bandwidth' in adaptation else ''
                    self.resultList[uniqueKey]['codecs'] = representation['@codecs'] if '@codecs' in adaptation else ''
                    self.resultList[uniqueKey]['frameRate'] = ''
                    self.resultList[uniqueKey]['width'] = ''
                    self.resultList[uniqueKey]['height'] = ''

                got_sound = True

            elif mimeType[0] == 'video':
                for representation in representations:
                    uniqueKey = str(video_id)+str(representation['@id'])
                    self.resultList[uniqueKey]= {}
                    self.resultList[uniqueKey]['video_id'] = video_id
                    self.resultList[uniqueKey]['mimeType'] = adaptation['@mimeType'] if '@mimeType' in adaptation  else ''
                    self.resultList[uniqueKey]['bandwidth'] = representation['@bandwidth'] if '@bandwidth' in representation else ''
                    self.resultList[uniqueKey]['codecs'] = representation['@codecs'] if '@codecs' in representation else ''
                    self.resultList[uniqueKey]['frameRate'] = representation['@frameRate'] if '@frameRate' in representation else ''
                    self.resultList[uniqueKey]['width'] = representation['@height'] if '@height' in representation  else ''
                    self.resultList[uniqueKey]['height'] = representation['@width'] if '@width' in representation else ''

    def saveResult(self):
        if len(self.resultList) > 0:
            self.updateProgress('SAVING')
            from project.models import VideoRepresentation
            from sqlalchemy.ext.compiler import compiles
            from sqlalchemy.sql.expression import Insert
            @compiles(Insert)
            def replace_string(insert, compiler, **kw):
                s = compiler.visit_insert(insert, **kw)
                if 'replace_string' in insert.kwargs:
                    return str(s).replace("INSERT",insert.kwargs['replace_string'])
                return s

            t0 = time.time()
            logger.info("save video MPD")
            #http://docs.sqlalchemy.org/en/rel_0_9/core/connections.html?highlight=engine#sqlalchemy.engine.Connection.execute
            db.session.execute(VideoRepresentation.__table__.insert(replace_string = 'INSERT OR REPLACE'),
                   [value for key,value in self.resultList.iteritems()]
                   )
            logger.info("Total time for " + str(len(self.resultList)) +" records " + str(time.time() - t0) + " secs")



