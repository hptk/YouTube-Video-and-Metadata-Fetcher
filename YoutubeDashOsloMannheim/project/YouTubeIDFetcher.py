import gevent.pool
from gevent.queue import JoinableQueue
from geventhttpclient import HTTPClient, URL

#import time
import json
import datetime

#from project import db

#from project.models import YoutubeVideo
numberHTTPClients = 50
numberClientConcurrent = 100

publishedBefore = datetime.datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0) -datetime.timedelta(days=30)
publishedAfter = publishedBefore - datetime.timedelta(days=7)
totalFrame = int((publishedBefore-publishedAfter).total_seconds())
secondsPerFrame = int(totalFrame/numberHTTPClients)


DEVELOPER_KEY = "AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"


countAll = 0
pageAll = 0
countRequests = 0
videoIDs = {}


def calculateTimeframe(publishedBefore,frame):
    return publishedBefore - datetime.timedelta(seconds=frame)

def formatDate(date):
    return date.strftime('%FT%TZ')

def buildRequest(publishedAfter,publishedBefore,pageToken=''):
    return URL("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=date&pageToken="+pageToken+"&publishedAfter="+formatDate(publishedAfter)+"&publishedBefore="+formatDate(publishedBefore)+"&type=video&key=AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8")
def printDateTuple(dateTuple):
    print dateTuple[0].strftime('%FT%TZ')+"\t"+dateTuple[1].strftime('%FT%TZ')

def makeRequest(publishedAfter,publishedBefore):
    global countAll, pageAll, videoIDs, countRequests, pool
    countRequests += 1
    request = buildRequest(publishedAfter,publishedBefore)
    print str(q.qsize())+" "+str(len(videoIDs))+" "+str(request)
    response = http.get(request.request_uri)
    result = json.load(response)
    
    if "items" in result:
        req_results = len(result['items'])
        countAll += req_results
        
        #do something with the data
        for item in result['items']:
            videoIDs[str(item['id']['videoId'])]=1
            #video = YoutubeVideo(
            #                id=item['id']
            #                )
            #try:
                #db.session.add(video)
                #db.session.commit()
                
            #except:
                #video already inserted
                #print "err"
                #pass
            #db.session.close()
        secondsTimeSpan = int((publishedBefore-publishedAfter).total_seconds())
        #slice the timeframe if has more pages and more results than 50 and the timespan is bigger than 1 (maybe there are more than 50 videos per second and it will result in a loop)
        if "nextPageToken" in result and req_results==50 and secondsTimeSpan > 1:
            pageAll += 1
            midDate = publishedAfter+(publishedBefore-publishedAfter)/2
            #print request
            #add new timeframes to queue
            q.put((publishedAfter,midDate-datetime.timedelta(seconds=1)))
            q.put((midDate,publishedBefore))
                
            

http = HTTPClient.from_url(URL("https://www.googleapis.com"), concurrency=numberClientConcurrent)

def worker(fetcher_id):
    while not q.empty():
        
        timeFrame = q.get()
        
        publishedBefore = timeFrame[1]
        publishedAfter = timeFrame[0]
        try:
            makeRequest(publishedAfter, publishedBefore)
        finally:
            q.task_done()

q = JoinableQueue()
            
# allow to run 20 greenlet at a time, this is more than concurrency
# of the http client but isn't a problem since the client has its own
# connection pool.
pool = gevent.pool.Pool(numberHTTPClients)
starttime = datetime.datetime.now()

fetcher_id = 0
#spawn first frames
tempTime = publishedBefore
for x in xrange(0,totalFrame/secondsPerFrame):
    tempTimeBefore = calculateTimeframe(tempTime,x*secondsPerFrame)
    tempTimeAfter = calculateTimeframe(tempTimeBefore,secondsPerFrame)
    #create disjunct timeframes, otherwise there are duplicated videoIDs
    tempTime = calculateTimeframe(tempTime,1)

    q.put((tempTimeAfter,tempTimeBefore))
    
    pool.spawn(worker,fetcher_id)
    fetcher_id += 1


pool.join()
http.close()

print str(totalFrame)+"\t"+str(secondsPerFrame)+"\t"+str(countAll)+"\t"+str(len(videoIDs))+"\t"+str(pageAll)+"\t"+str(countRequests)+"\t"+str((datetime.datetime.now()-starttime).total_seconds())
