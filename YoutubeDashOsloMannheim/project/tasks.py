from YouTubeIDFetcherClass import YouTubeIDFetcher
from project import celery
@celery.task(bind=True)
def fetch(self):
    fetcher = YouTubeIDFetcher(50,50,self)
    return fetcher.work()