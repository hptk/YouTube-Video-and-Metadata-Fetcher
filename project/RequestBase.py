import logging
import gevent.pool
from gevent.queue import JoinableQueue
from geventhttpclient import HTTPClient, URL
import json
from _ssl import SSLError
from pprint import pprint
from gevent import monkey
import random
monkey.patch_time()
logger = logging.getLogger('tasks')

class RequestBase(object):
    def __init__(self,url,parameter,HTTPClients,ClientConnectionPool,task=None):

        if task is not None:
            self.celeryTask = task
            self.celeryTaskId = task.request.id
        else:
            self.celeryTask = None

        self.parameter = parameter
        self.url = url
        self.numberHTTPClients = HTTPClients
        self.numberClientConnectionPool = ClientConnectionPool

        self.http = HTTPClient.from_url(URL(url),concurrency=self.numberClientConnectionPool)
        self.clientPool = gevent.pool.Pool(self.numberHTTPClients)
        self.workQueue = JoinableQueue()

        self.resultList = {}
        self.workQueueMax = 0
        self.workQueueDone = 0
        self.countRequests = 0
        self.status_codes = {}
        self.status_codes_count = {}
        self.meta = {}

        self.greenletList = {}
        self.initAdditionalStructures()
        self.progressMeta = None

        self.exitFlag = False
        self.pauseRequests = False


    def destroy(self):
        self.http.close()

    def initAdditionalStructures(self):
        pass

    def destroyAdditionstrucutres(self):
        pass

    def getProgress(self):
        return self.meta

    def updateProgress(self,state="PROGRESS"):
        '''Updates the status'''
        self.meta = {'state':state,'workQueueDone': self.workQueueDone, 'workQueueMax': self.workQueueMax,'current':len(self.resultList),'workQueue':self.workQueue.qsize(),'requests':self.countRequests}

        #iterate over status_codes dict and save the queue size. may be not the best solution from performance view
        for code,queue in self.status_codes.iteritems():
            self.status_codes_count[code] = queue.qsize()
        self.meta['status_codes'] = self.status_codes_count
        if self.celeryTask is not None:
            self.celeryTask.update_state(task_id=self.celeryTaskId,state=state,meta=self.meta)

    def worker(self,http,clientId):
        while not self.workQueue.empty() or self.exitFlag:
                try:
                    code = self.makeRequest(http,self.getWorkQueueItem())
                finally:
                    self.workQueue.task_done()
      
    def stop(self):
        self.exitFlag=True

    def buildRequestURL(self,workQueueItem):
        '''Function used to build the request URL from a workingQueue item'''
        pass

    def handleRequestSuccess(self,workQueueItem, result):
        '''Required function, called after every successful request'''
        pass

    def handleRequestFailure(self,result):
        '''Function called after a failed request. For example error code 404'''
        pass

    def makeRequest(self,http,workQueueItem):
        '''Makes the request to and '''
        url_string = self.buildRequestURL(workQueueItem)

        self.countRequests += 1
        try:
            
            response = http.get(URL(url_string).request_uri)
            statusCode = response.status_code

            #create a new queue if the response status_code did not exist and adds the item to the queue
            if str(statusCode) not in self.status_codes:
                self.status_codes[str(statusCode)] = JoinableQueue()
            self.status_codes[str(statusCode)].put(workQueueItem)

            try:
                self.handleRequestSuccess(workQueueItem,response)
            except SSLError,e:
                print e

            return statusCode
        except Exception,e:
            self.putWorkQueueItem(workQueueItem)



    def putWorkQueueItem(self,item):
        '''Puts a single item on the workingQueue and calculates the maximum of the global workingQueue'''
        self.workQueue.put(item)
        if self.workQueueMax<self.workQueue.qsize():
            self.workQueueMax=self.workQueue.qsize()

    def getWorkQueueItem(self):
        '''Returns a single item from the working queue and removes it'''
        self.workQueueDone+=1
        self.updateProgress()
        return self.workQueue.get()

    def initWorkQueue(self):
        '''Required function which is called at the beginning in order to set up the initial workingQueue'''
        pass

    def saveResult(self):
        '''Function called after all requests are done. For example can be used to modify/save the results'''
        pass

    def returnResult(self):
        '''returns the meta result, which is set by updateProgress'''
        self.meta['result']=len(self.resultList)
        return self.meta

    def setUpWorkPool(self):
        '''Sets up the worker pool of the HTTP clients.'''
        HTTPClientId = 0
        while HTTPClientId < self.numberHTTPClients:
            self.greenletList[str(HTTPClientId)] = self.clientPool.spawn(self.worker,self.http,HTTPClientId)
            HTTPClientId += 1

        self.clientPool.join()

    def work(self):
        logger.info("Start up the work")
        try:
            logger.info("Initialize WorkQueue")
            self.initWorkQueue()
            logger.info("Create HTTPClient Pool")
            self.setUpWorkPool()
        finally:
            logger.info("Save Results")
            self.saveResult()
            self.updateProgress("DONE")
            self.destroy()
            self.destroyAdditionstrucutres()
        return self.returnResult()



