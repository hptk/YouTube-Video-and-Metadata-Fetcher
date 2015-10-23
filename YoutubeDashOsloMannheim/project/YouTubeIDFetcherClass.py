import gevent.pool
from gevent.queue import JoinableQueue
from geventhttpclient import HTTPClient, URL
from threading import Timer
import json
import datetime

#a thread class which is used to update the state of the task only at each interval and not everytime in order to slow down the background changes since the UI only fetches the state every 1 second
#no need to call start, thread is self starting
#start and stop are save to call multipletimes even if the timer already started/stopped
#function can have positional and named arguments
#you can change interval anytime, it will be effective after next run. same for args,kwards and even function
class updateState(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()
        
    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)
        
    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval,self._run)
            self._timer.start()
            self.is_running = True
            
    def stop(self):
        self._timer.cancel()
        self.is_running = False
        
#from project import db
#from project.models import YoutubeVideo
class YouTubeIDFetcher():
    def __init__(self,HTTPClients,ClientConnectionPool,task):
        self.celeryTask = task
        self.task_id = task.request.id

        self.numberHTTPClients = HTTPClients
        self.numberClientConnectionPool = ClientConnectionPool
        # allow to run 20 greenlet at a time, this is more than concurrency
        # of the http client but isn't a problem since the client has its own
        # connection pool.
        self.http = HTTPClient.from_url(URL("https://www.googleapis.com"), concurrency=self.numberClientConnectionPool)
        self.pool = gevent.pool.Pool(self.numberHTTPClients)
        self.q = JoinableQueue()
        self.countAll = 0
        self.countRequests = 0
        self.videoIDs = {}
                
        self.publishedBefore = datetime.datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0) -datetime.timedelta(days=30)
        self.publishedAfter = self.publishedBefore - datetime.timedelta(days=1)
        self.totalFrame = int((self.publishedBefore-self.publishedAfter).total_seconds())
        self.secondsPerFrame = int(self.totalFrame/self.numberHTTPClients)
        self.initFrames = int(self.totalFrame/self.secondsPerFrame)
        self.qMax = 0
        self.qWorked = 0
        
        #self.stateUpdater = updateState(1,self.celeryTask.update_state,task_id=self.task_id,state='PROGRESS',meta={'workedRequests': self.qWorked, 'maxRequests': self.qMax,'current':len(self.videoIDs),'queueSize':self.q.qsize()})
        #self.stateUpdater.stop()
    
    def calculateTimeframe(self,publishedBefore,frame):
        return publishedBefore - datetime.timedelta(seconds=frame)

    def formatDate(self,date):
        return date.strftime('%FT%TZ')

    def buildRequest(self,publishedAfter,publishedBefore):
        return URL("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=date&publishedAfter="+self.formatDate(publishedAfter)+"&publishedBefore="+self.formatDate(publishedBefore)+"&type=video&key=AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8")


    def makeRequest(self,publishedAfter,publishedBefore):
    
        self.countRequests += 1
        request = self.buildRequest(publishedAfter,publishedBefore)
        #print str(self.q.qsize())+"\t"+str(len(self.videoIDs))+"\t"+str(request)
        response = self.http.get(request.request_uri)
        result = json.load(response)
        
        if "items" in result:
            req_results = len(result['items'])
            self.countAll += req_results
            
            #do something with the data
            for item in result['items']:
                self.videoIDs[str(item['id']['videoId'])]=1
                
            secondsTimeSpan = int((publishedBefore-publishedAfter).total_seconds())
            #slice the timeframe if has more pages and more results than 50 and the timespan is bigger than 1 (maybe there are more than 50 videos per second and it will result in a loop)
            if "nextPageToken" in result and req_results==50 and secondsTimeSpan > 1:
                midDate = publishedAfter+(publishedBefore-publishedAfter)/2
                #print request
                #add new timeframes to queue
                self.q.put((publishedAfter,midDate-datetime.timedelta(seconds=1)))
                self.q.put((midDate,publishedBefore))

    def worker(self,fetcher_id):
        while not self.q.empty():
            
            self.setQueueSizeWorked(1)
            #print str(self.getCurrentProcess())
            #self.task.update_state(state='PROGRESS',meta={'worked': self.qWorked, 'max': self.qMax})
            
            timeFrame = self.q.get()
            
            publishedBefore = timeFrame[1]
            publishedAfter = timeFrame[0]
            try:
                self.makeRequest(publishedAfter, publishedBefore)
            finally:
                self.q.task_done()
        
        
    def getQueueSizeWorked(self):
        return self.qWorked
    
    def setQueueSizeWorked(self,worked):
        #print self.qWorked
        self.qWorked += int(worked)
        if self.qMax<self.q.qsize():
            self.qMax=self.q.qsize()
        self.celeryTask.update_state(task_id=self.task_id,state='PROGRESS',meta={'workedRequests': self.qWorked, 'maxRequests': self.qMax,'current':len(self.videoIDs),'queueSize':self.q.qsize()})
        
    def getCurrentProcess(self):
        return str(self.qWorked/float(self.qWorked+self.q.qsize()))+"\t"+str(self.qMax)+"\t"+str(self.qWorked)+"\t"+str(len(self.videoIDs))
        
    def work(self):
        try:
            #self.stateUpdater.start()
            #starttime = datetime.datetime.now()
            #print self.getFrames()
            fetcher_id = 0
            #spawn first frames
            tempTime = self.publishedBefore
            for x in xrange(0,self.initFrames):
                tempTimeBefore = self.calculateTimeframe(tempTime,x*self.secondsPerFrame)
                tempTimeAfter = self.calculateTimeframe(tempTimeBefore,self.secondsPerFrame)
                #create disjunct timeframes, otherwise there are duplicated videoIDs
                tempTime = self.calculateTimeframe(tempTime,1)
                self.q.put((tempTimeAfter,tempTimeBefore))
    
                self.pool.spawn(self.worker,fetcher_id)
                fetcher_id += 1

            self.pool.join()
        finally:
            self.http.close()
            #self.stateUpdater.stop();
            return {'result':len(self.videoIDs)}
            #print str(self.totalFrame)+"\t"+str(self.secondsPerFrame)+"\t"+str(self.countAll)+"\t"+str(len(self.videoIDs))+"\t"+str(self.pageAll)+"\t"+str(self.countRequests)+"\t"+str((datetime.datetime.now()-starttime).total_seconds())
