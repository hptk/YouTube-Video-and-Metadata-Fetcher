from YouTubeIDFetcher import YouTubeIDFetcher
from YouTubeMetaFetcher import YouTubeMetaFetcher
from YouTubeMPDFetcher import YouTubeMPDFetcher
from YouTubeCommentFetcher import YouTubeCommentFetcher
from project import celery
from project import db
from celery.signals import task_prerun
import json
import logging
logger = logging.getLogger('tasks')
@task_prerun.connect
def celery_prerun(*args, **kwargs):
    with celery.app.app_context():
        pass

@celery.task(bind=True)
def fetch(self,queryId):
    with celery.app.app_context():
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"IDFetcher")
        query.tasks.append(current_task)
        db.session.commit()
        parameter = {}
        parameter['queryId'] = queryId
        parameter['queryRaw'] = query.queryRaw
        logger.info("Start fetching ids for query id :"+str(parameter['queryId'])+" with parameter: "+parameter['queryRaw'])
        fetcher = YouTubeIDFetcher("https://www.googleapis.com/youtube/v3/search",parameter,50,50,self)

        result = fetcher.work()
        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result


@celery.task(bind=True)
def meta(self,queryId):
    with celery.app.app_context():
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"MetaFetcher")
        query.tasks.append(current_task)
        db.session.commit()

        fetcher = YouTubeMetaFetcher("https://www.googleapis.com/youtube/v3/videos",queryId,50,50,self)
        result = fetcher.work()

        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result


@celery.task(bind=True)
def manifest(self,queryId):
    with celery.app.app_context():
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"ManifestFetcher")
        query.tasks.append(current_task)
        db.session.commit()

        fetcher = YouTubeMPDFetcher("https://www.youtube.com/get_video_info",queryId,50,50,self)
        result = fetcher.work()

        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result


@celery.task(bind=True)
def comments(self,queryId,parameters):
    with celery.app.app_context():
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"CommentFetcher")
        query.tasks.append(current_task)
        db.session.commit()
        parameter = {}
        parameter['queryId'] = queryId
        parameter['get_replies'] = False
        fetcher = YouTubeCommentFetcher('https://www.googleapis.com/youtube/v3',parameter, 50, 50, self)
        result = fetcher.work()

        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result
