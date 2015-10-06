#!/usr/bin/python

import Queue
import threading
import time
import urllib2, urllib, ssl
import json
import datetime
from elasticsearch import Elasticsearch

exitFlag = 0

DEVELOPER_KEY = "AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"
numberThreads = 100

threadList = []
timeFrameList = []
#take secondsPerFrame big as possible in order to have a total of 0 pages
secondsPerFrame = (86400*24)/1024
totalFrame = 86400*24
videoIDs = {}
pageToken = ""
publishedBefore = datetime.datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-datetime.timedelta(days=100)
publishedAfter = None
countAll = 0
pageAll = 0
countRequests = 0
es = Elasticsearch()

def calculateTimeframe(publishedBefore,frame):
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
    return "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=date&pageToken="+pageToken+"&publishedAfter="+publishedAfter+"&publishedBefore="+publishedBefore+"&type=video&key=AIzaSyBlO0GfmL5LuRJoVlRhMVM8VjViE5BAAs8"

def printDateTuple(dateTuple):
    print dateTuple[0].strftime('%FT%TZ')+"\t"+dateTuple[1].strftime('%FT%TZ')

def req(publishedAfter,publishedBefore,pageToken="",page=0,results=0):
	global es, countAll, pageAll, videoIDs, countRequests
	countRequests += 1
	request = buildRequest(publishedAfter,publishedBefore,pageToken)
	try: 
		result = urllib2.urlopen(request,timeout=2)
	except urllib2.URLError as e:
		if hasattr(e,"reason"):
			print e.reason
			doc = {
				"reason": e.reason,
				"request": request,
			}
		elif hasattr(e,"code"):
			print e.code
			doc = {
				"error_code": e.code,
				"request": request,
			}
		es.index(index="youtubetestindexerror",doc_type="URLError",body=doc)
	except urllib2.HTTPError as e:
		doc = {
			"error_code": e.code,
			"request": request,
		}
		es.index(index="youtubetestindexerror",doc_type="HTTPError",body=doc)
	except ssl.SSLError as e:
		print request
    #except ssl.SSLError as e:
    #    doc = {
    #        "reason": e.reason,
    #        "request": request, 
    #    }
    #    es.index(index="youtubetestindexerror",doc_type="SSLError",body=doc)
	else: 
		jsonResult = json.loads(result.read())
		if "items" in jsonResult:
			req_results = len(jsonResult['items'])
			results += req_results
			for item in jsonResult['items']:
				videoIDs[str(item['id']['videoId'])]=1
				doc = {
					"title": item['snippet']['title'],
					"channelId": item['snippet']['channelId'],
					"description": item['snippet']['description'],
					"channelTitle": item['snippet']['channelTitle'],
					"publishedAt": item['snippet']['publishedAt'],
					"timestamp": datetime.datetime.now(),
				}
				es.index(index="youtubetestindex4",doc_type="video",id=item['id']['videoId'],body=doc)
			if "nextPageToken" in jsonResult and req_results==50:
				page += 1
				req(publishedAfter,publishedBefore,jsonResult['nextPageToken'],page,results)
			else:
				#print str(publishedAfter)+"\t"+str(publishedBefore)+"\t"+str(results)+"\t"+str(page)
				countAll += results
				pageAll += page

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

for x in xrange(0,totalFrame/secondsPerFrame):
    tempTimeBefore = calculateTimeframe(tempTime,x*secondsPerFrame)
    tempTimeAfter = calculateTimeframe(tempTimeBefore,secondsPerFrame)
    #create disjunct timeframes, otherwise there are duplicated videoIDs
    tempTime = calculateTimeframe(tempTime,1)

    #for y in xrange(0,10):
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

#print "counted "+str(countAll)
#print "unique "+str(len(videoIDs))
#print "global number pages (maybe best if 0)"+str(pageAll)
print str(totalFrame)+"\t"+str(secondsPerFrame)+"\t"+str(countAll)+"\t"+str(len(videoIDs))+"\t"+str(pageAll)+"\t"+str(countRequests)
#timeNeeded = millis()-starttime
#requestPerSecond = int(numberVideoIDs/(timeNeeded/1000))
#print str(numberThreads)+" Threads: "+str(numberVideoIDs)+" request in "+str(timeNeeded)+" ms => "+str(requestPerSecond)+" request/second"
