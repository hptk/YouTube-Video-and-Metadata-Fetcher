from YouTubeIDFetcher import YouTubeIDFetcher
from project import celery
@celery.task(bind=True)
def fetch(self,parameter):
    fetcher = YouTubeIDFetcher("https://www.googleapis.com/youtube/v3/search",parameter,50,50,self)
    return fetcher.work()