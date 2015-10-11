from pprint import pprint
from urllib2 import urlopen
import json
import sys

_COMMENTTHREAD_MAXRESULTS = 100
_COMMENTS_MAXRESULTS = 100
_VIDEOS_MAXRESULTS = 50
_TESTVID = "JjDsP5n2kSM"

class APIRequestString:
    def __init__(self, url, resource, key):
        self.root = url + '/' + resource + '?'
        self.properties = {'key': [key]}

    def add(self, property_name, *property_values):
        try:
            self.properties[property_name] += property_values
        except KeyError:
            self.properties[property_name] = property_values

    def build(self):
        request_string = self.root + '&'.join(map(lambda name: name + '=' + ','.join(self.properties[name]), self.properties.keys()))
        return request_string

class YouTubeAPI:
    def __init__(self, api_url, api_key):
        self.url = api_url
        self.key = api_key

    def makeRequest(self, request):
        return json.loads(urlopen(request.build()).read().decode())

    def getReplies(self, comment_thread_id, results=[], page_token='', depth=1):
        request = APIRequestString(self.url, 'comments', self.key)
        request.add('part', 'snippet')
        request.add('maxResults', str(_COMMENTS_MAXRESULTS))
        request.add('parentId', comment_thread_id)
        if page_token != '':
            request.add('pageToken', page_token)

        result = self.makeRequest(request)
        if not result['items']:
            return results

        results += result['items']

        # The API does not return the ['pageInfo']['totalResults'] properly,
        # thus we have to manually check the no. of comments returned
        if len(result['items']) == result['pageInfo']['resultsPerPage']:
            try:
                return self.getReplies(comment_thread_id, results, result['nextPageToken'], depth+1)
            except KeyError:
                pass

        return results


    def getComments(self, video_id, results=[], page_token='', depth=1, get_replies=False):
        request = APIRequestString(self.url, 'commentThreads', self.key)
        request.add('part', 'snippet')
        request.add('maxResults', str(_COMMENTTHREAD_MAXRESULTS))
        request.add('videoId', video_id)
        if page_token != '':
            request.add('pageToken', page_token)

        result = self.makeRequest(request)
        if not result['items']:
            return results

        if get_replies:
            # Iterate over commentThread resources and fill their 'replies' property
            for comment_thread in result['items']:
                if comment_thread['snippet']['totalReplyCount'] > 0:
                    comment_thread['replies'] = {'comments': self.getReplies(comment_thread['id'])}

        results += result['items']

        if result['pageInfo']['totalResults'] == result['pageInfo']['resultsPerPage']:
            try:
                return self.getComments(video_id, results, result['nextPageToken'], depth+1, get_replies)
            except KeyError:
                pass

        return results
 
    def getVideosAtTime(self, published_after, published_before, results=[], page_token=''):
        request = APIRequestString(self.url, 'search', self.key)
        request.add('part', 'snippet')
        request.add('maxResults', _VIDEOS_MAXRESULTS)
        request.add('order', 'date')
        request.add('publishedAfter', published_after)
        request.add('publishedBefore', published_before)
        request.add('type', video)
        if page_token != '':
            request.add('pageToken', page_token)
    
        result = self.makeRequest(request)
        if not result['items']:
            return results

        results += result['items']

        if result['pageInfo']['totalResults'] == result['pageInfo']['resultsPerPage']:
            try:
                return self.getVideosAtTime(self, published_after, published_before, results, result['nextPageToken'])
            except KeyError:
                pass

        return results

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    with open('APIkey') as apikeyfile:
        test = YouTubeAPI('https://www.googleapis.com/youtube/v3',
                          apikeyfile.readline().rstrip())

    pprint(test.getComments(_TESTVID, get_replies=True))
    #print(test.getComments('h1Uxlnv12NY'))
