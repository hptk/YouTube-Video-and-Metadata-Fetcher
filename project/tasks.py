from YouTubeIDFetcher import YouTubeIDFetcher
from project import celery
from project import db
from celery.signals import task_prerun
import json
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
        
        fetcher = YouTubeIDFetcher("https://www.googleapis.com/youtube/v3/search",query.get_queryRaw(),50,50,self)
    
        result = fetcher.work()
        current_task.result = json.dumps(result) 
        current_task.state = result['state']
        db.session.commit()
        return result