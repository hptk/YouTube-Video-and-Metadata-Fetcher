#!/usr/bin/python

import Queue
import threading
import time
import urllib2, urllib
import sys, getopt
import json
import datetime


exitFlag = 0

DEVELOPER_KEY = "AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"
numberThreads = 50

threadList = []
idList = []

pageToken = ""
publishedBefore = datetime.datetime.utcnow().replace(minute=0,second=0,microsecond=0)
publishedAfter = None
secondsFrame = 1

def calculateTimeframe(startDate):
    global publishedBefore, publishedAfter, secondFrame
    publishedBefore = startDate - datetime.timedelta(seconds=(secondsFrame-1))
    publishedAfter = publishedBefore - datetime.timedelta(seconds=secondsFrame)

    
calculateTimeframe(publishedBefore)

results = 0
page = 0
options, remainder = getopt.getopt(sys.argv[1:], 't:v', [
                                                        'threads=',
                                                        'videos=',
                                                        ])
for opt, arg in options:
    if opt in ('-t', '--threads'):
        numberThreads = int(arg)
    elif opt in ('-v','--videos'):
        numberVideoIDs = int(arg)


class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        makeRequest(self.name, self.q)

def buildRequest(pageToken):
    return "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=date&pageToken="+pageToken+"&publishedAfter="+publishedAfter.strftime('%FT%TZ')+"&publishedBefore="+publishedBefore.strftime('%FT%TZ')+"&type=video&fields=items%2Fid%2CnextPageToken%2CpageInfo%2CprevPageToken%2CtokenPagination&key=AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"



def makeRequest(threadName, q):
    global results, page, pageToken
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            #print workQueue.qsize()
            pageToken = q.get()
            #print workQueue.qsize()
            queueLock.release()
            starttime = millis()
            jsonResult = json.loads(urllib2.urlopen(buildRequest(pageToken)).read())
            if "items" in jsonResult:
                results += len(jsonResult['items'])
            if "nextPageToken" in jsonResult:
                nextPage = jsonResult['nextPageToken']
                queueLock.acquire()
                workQueue.put(nextPage)
                queueLock.release()
            else:
                calculateTimeframe(publishedAfter)
                print str(publishedAfter)+"\t"+str(publishedBefore)+"\t"+str(results)
                pageToken = ""
                page = 0
                results = 0
                queueLock.acquire()
                workQueue.put(pageToken)
                queueLock.release()

            #print "%s processing %s in %s ms: page %i=%i results" % (threadName, pageToken,str(millis()-starttime),page,results)
        else:
            
            queueLock.release()

def millis():
    return (round(time.time()*1000))


for x in xrange(0,numberThreads):
    threadList.append(x)



idList.append(pageToken)

queueLock = threading.Lock()
workQueue = Queue.Queue(0)
threads = []
threadID = 0

# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# Fill the queue
queueLock.acquire()
for id in idList:
    workQueue.put(id)

starttime = millis()
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
#exitFlag = 1

# Wait for all threads to complete
for t in threads:
    t.join()

#timeNeeded = millis()-starttime
#requestPerSecond = int(numberVideoIDs/(timeNeeded/1000))
#print str(numberThreads)+" Threads: "+str(numberVideoIDs)+" request in "+str(timeNeeded)+" ms => "+str(requestPerSecond)+" request/second"
