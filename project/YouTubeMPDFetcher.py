import time
import xmltodict
import logging
from project.models import VideoRepresentation
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert
from RequestBase import RequestBase
from urllib2 import urlopen, unquote;
from urlparse import parse_qs;
from project import db
from project.models import QueryVideoMM
logger = logging.getLogger('tasks')

class YouTubeMPDFetcher(RequestBase):

    def buildRequestURL(self, work_queue_item):
        return self.url + '?video_id=' + work_queue_item

    def initWorkQueue(self):
        video_ids = db.session.query(QueryVideoMM).filter_by(youtube_query_id=self.parameter).all()
        for video in video_ids:
            self.putWorkQueueItem(video.video_id)

    def handleRequestSuccess(self, work_queue_item, response):
        video_id = work_queue_item

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
            representations = adaptation['Representation']
            if not isinstance(representations, list):
                representations = [representations]
            res = {}
            if mimeType[0] == 'audio':
                for representation in representations:
                    uniqueKey = str(video_id) + str(representation['@id'])
                    res['video_id'] = video_id
                    res['mimeType'] = adaptation.get('@mimeType') or ''
                    res['bitrate'] = representation.get('@bandwidth') or ''
                    res['codec'] = representation.get('@codecs') or ''
                    res['framerate'] = ''
                    res['width'] = ''
                    res['height'] = ''
                    self.resultList[uniqueKey] = res
            elif mimeType[0] == 'video':
                for representation in representations:
                    uniqueKey = str(video_id) + str(representation['@id'])
                    res['video_id'] = video_id
                    res['mimeType'] = adaptation.get('@mimeType') or ''
                    res['bitrate'] = representation.get('@bandwidth') or ''
                    res['codec'] = representation.get('@codecs') or ''
                    res['framerate'] = representation.get('@frameRate') or ''
                    res['width'] = representation.get('@height') or ''
                    res['height'] = representation.get('@width') or ''
                    self.resultList[uniqueKey] = res

    def saveResult(self):
        if len(self.resultList) > 0:
            self.updateProgress('SAVING')
            @compiles(Insert)
            def replace_string(insert, compiler, **kw):
                s = compiler.visit_insert(insert, **kw)
                if 'replace_string' in insert.kwargs:
                    return str(s).replace("INSERT", insert.kwargs['replace_string'])
                return s

            t0 = time.time()
            logger.info("save video MPD")
            #http://docs.sqlalchemy.org/en/rel_0_9/core/connections.html?highlight=engine#sqlalchemy.engine.Connection.execute
            db.session.execute(VideoRepresentation.__table__.insert(replace_string = 'INSERT OR REPLACE'),
                    [value for key, value in self.resultList.iteritems()]
                    )
            logger.info("Total time for " + str(len(self.resultList)) + " records " + str(time.time()-t0) + " secs")



