#!/usr/bin/python

import Queue
import threading
import time
import urllib2, urllib
import json
import datetime


exitFlag = 0

DEVELOPER_KEY = "AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"
numberThreads = 100

threadList = []
timeFrameList = []

pageToken = ""
publishedBefore = datetime.datetime.utcnow().replace(minute=0,second=0,microsecond=0)-datetime.timedelta(days=20)
publishedAfter = None


def calculateTimeframe(publishedBefore,frame=1):
    return publishedBefore - datetime.timedelta(seconds=frame)
 


class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        makeRequest(self.name, self.q)

def formatDate(date):
    return date.strftime('%FT%TZ')

def buildRequest(publishedAfter,publishedBefore,pageToken):
    return "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=date&pageToken="+pageToken+"&publishedAfter="+publishedAfter+"&publishedBefore="+publishedBefore+"&type=video&fields=items%2Fid%2CnextPageToken%2CpageInfo%2CprevPageToken%2CtokenPagination&key=AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"

def printDateTuple(dateTuple):
    print dateTuple[0].strftime('%FT%TZ')+"\t"+dateTuple[1].strftime('%FT%TZ')

def req(publishedAfter,publishedBefore,pageToken="",page=0,results=0):
    jsonResult = json.loads(urllib2.urlopen(buildRequest(publishedAfter,publishedBefore,pageToken)).read())
    if "items" in jsonResult:
        results += len(jsonResult['items'])
    if "nextPageToken" in jsonResult:
        page += 1
        req(publishedAfter,publishedBefore,jsonResult['nextPageToken'],page,results)
    else:
        print str(publishedAfter)+"\t"+str(publishedBefore)+"\t"+str(results)+"\t"+str(page)

def makeRequest(threadName, q, pageToken="", page=0, results=0):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            timeFrame = q.get()
            queueLock.release()
            publishedBefore = formatDate(timeFrame[1])
            publishedAfter = formatDate(timeFrame[0])

            req(publishedAfter,publishedBefore,pageToken)
            
        else:
            queueLock.release()

for x in xrange(0,numberThreads):
    threadList.append(x)

tempTime = publishedBefore

for x in xrange(0,2):
    tempTimeBefore = calculateTimeframe(tempTime,x)
    tempTimeAfter = calculateTimeframe(tempTimeBefore)
    tempTime = calculateTimeframe(tempTime)
    #for y in xrange(0,100):
    #    timeFrameList.append((tempTimeAfter,tempTimeBefore))
    timeFrameList.append((tempTimeAfter,tempTimeBefore))

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
for timeFrame in timeFrameList:
    workQueue.put(timeFrame)

queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
    t.join()

#timeNeeded = millis()-starttime
#requestPerSecond = int(numberVideoIDs/(timeNeeded/1000))
#print str(numberThreads)+" Threads: "+str(numberVideoIDs)+" request in "+str(timeNeeded)+" ms => "+str(requestPerSecond)+" request/second"
